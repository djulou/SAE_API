import pandas as pd
import ast
from sqlalchemy import text
from map import map_langue_iso, map_license,map_langue_iso, map_langue_to_iso, map_album_type
from fonction import _random_hash, _encode_gender, _interval_to_date, convertir_duree


def preparer_table_users(df_source):
    """
    Transforme le CSV complet en DataFrame formaté pour la table SQL 'users'.
    Ajout : Génération automatique de 'pseudo' et 'image'.
    """
    
    # 1. On travaille sur une copie
    df = df_source.copy()
    n = len(df)

    # 2. Création du DataFrame final
    users = pd.DataFrame()

    # ID SQL (commence à 1)
    users['user_id'] = range(1, n + 1)

    # Génération des champs textes basiques
    users["email"] = [f"user{i}@anon.com" for i in range(n)]
    users["user_login"] = [f"user_{i:04d}" for i in range(n)]
    users["user_mdp"] = [ _random_hash(f"pass_{i}") for i in range(n) ]
    users["pseudo"] = [f"User_{i}" for i in range(n)]
    users["image"] = [f"image_{i}.png" for i in range(n)]

    col_sexe = "Quel est votre sexe ?"
    if col_sexe in df.columns:
        users["user_gender"] = df[col_sexe].apply(_encode_gender)
    else:
        users["user_gender"] = "O"

    col_age = "Quel est votre âge ?"
    if col_age in df.columns:
        users["birth_year"] = df[col_age].apply(_interval_to_date)
    else:
        users["birth_year"] = None

    col_situation = "Quelle est votre situation  ? "
    if col_situation in df.columns:
        users["situation_name"] = df[col_situation]

    col_freq = "À quelle fréquence écoutez-vous de la musique ?"
    if col_freq in df.columns:
        users["frequency_interval"] = df[col_freq]

    return users

def preparer_table_languages(df_source):
    languages = df_source.copy()
    languages['language_id'] = languages['track_language_code'].map(map_langue_iso)
    if 'language_name' not in languages.columns:
        languages['language_name'] = languages['track_language_code']
    cols_a_garder = ["language_id", "language_name"]
    languages = languages[cols_a_garder].dropna(subset=['language_id'])
    languages = languages.drop_duplicates(subset=['language_id'])
    return languages

def preparer_table_licenses(df_source):
    licenses = df_source[['license_title']].copy()
    licenses['license_name_clean'] = licenses['license_title'].astype(str).str.lower().str.strip()
    licenses['license_id'] = licenses['license_name_clean'].map(map_license)
    licenses = licenses.dropna(subset=['license_id'])
    licenses['license_id'] = licenses['license_id'].astype(int)
    licenses['license_name'] = licenses['license_title']
    cols_finales = ["license_id", "license_name"]
    licenses = licenses[cols_finales].drop_duplicates(subset=['license_id'])
    return licenses

def preparer_table_album_type(df_source):
    types = df_source[['album_type']].copy()
    types['type_temp'] = types['album_type'].fillna("").astype(str).str.lower().str.strip()
    types['type_id'] = types['type_temp'].map(map_album_type)
    types['type_name'] = types['album_type'].fillna("")
    types = types.dropna(subset=['type_id'])
    types['type_id'] = types['type_id'].astype(int)
    cols_finales = ["type_id", "type_name"]
    types = types[cols_finales].drop_duplicates(subset=['type_id'])
    types = types.sort_values(by='type_id')
    return types

import pandas as pd

def preparer_table_tags_globale(df_tracks, df_albums, df_artists):
    t_tracks = df_tracks[['tags']].copy()
    t_albums = df_albums[['tags']].copy()
    t_artists = df_artists[['tags']].copy()

    all_tags = pd.concat([t_tracks, t_albums, t_artists], ignore_index=True)

    all_tags['tag_clean'] = all_tags['tags'].fillna("").astype(str).str.replace(r'[\[\]\'"]', '', regex=True)
    
    all_tags['tag_clean'] = all_tags['tag_clean'].str.split(',')
    all_tags = all_tags.explode('tag_clean')

    all_tags['tag_name'] = all_tags['tag_clean'].str.lower().str.strip()

    tags_final = all_tags[all_tags['tag_name'] != ""]
    tags_final = tags_final[['tag_name']].drop_duplicates().sort_values('tag_name')

    tags_final['tag_id'] = range(1, len(tags_final) + 1)

    return tags_final[['tag_id', 'tag_name']]

def preparer_table_genres(df_source):
    """
    Prépare la table Genre.
    Gère la colonne 'genre_parent_id' pour définir la hiérarchie.
    """
    print("--- Préparation de la table Genre ---")
    
    # 1. Sélection des colonnes utiles
    # Ton CSV a : genre_id, genre_color, genre_handle, genre_parent_id, genre_title
    cols_source = ["genre_id", "genre_parent_id", "genre_title", "genre_handle"]
    
    # On vérifie qu'elles sont là
    cols_presentes = [c for c in cols_source if c in df_source.columns]
    genres = df_source[cols_presentes].copy()

    # 2. Nettoyage ID (Clé primaire)
    genres['genre_id'] = pd.to_numeric(genres['genre_id'], errors='coerce')
    genres = genres.dropna(subset=['genre_id'])
    genres['genre_id'] = genres['genre_id'].astype(int)
    
    # 3. Nettoyage Parent ID
    # Convertit les vides et les erreurs en NaN, puis en type Int64 (qui accepte les NULLs)
    genres['genre_parent_id'] = pd.to_numeric(genres['genre_parent_id'], errors='coerce')
    
    # Cas particulier : Parfois le CSV met '0' pour dire "Pas de parent". 
    # En SQL, "Pas de parent" doit être NULL, pas 0 (car le genre 0 n'existe pas).
    genres.loc[genres['genre_parent_id'] == 0, 'genre_parent_id'] = None
    
    # On s'assure qu'un genre n'est pas son propre parent (boucle infinie)
    genres.loc[genres['genre_parent_id'] == genres['genre_id'], 'genre_parent_id'] = None

    genres['genre_parent_id'] = genres['genre_parent_id'].astype('Int64')

    # 4. Nettoyage Textes
    if 'genre_title' in genres.columns:
        genres['genre_title'] = genres['genre_title'].fillna("").astype(str).str.strip().str.slice(0, 255)
    
    if 'genre_handle' in genres.columns:
        genres['genre_handle'] = genres['genre_handle'].fillna("").astype(str).str.strip().str.slice(0, 255)

    # 5. GESTION DES PARENTS MANQUANTS (Astuce pour éviter l'erreur Foreign Key)
    # Si le genre 1 a pour parent 38, mais que 38 n'est pas dans le CSV, l'insertion plantera.
    # On vérifie que tous les parents existent.
    ids_existants = set(genres['genre_id'])
    parents_demandes = set(genres['genre_parent_id'].dropna())
    
    parents_manquants = parents_demandes - ids_existants
    
    if parents_manquants:
        lignes_manquantes = []
        for pid in parents_manquants:
            lignes_manquantes.append({
                'genre_id': int(pid),
                'genre_parent_id': None, # On le met à la racine par sécurité
                'genre_title': f"Genre {int(pid)}",
                'genre_handle': f"unknown_{int(pid)}"
            })
        df_manquants = pd.DataFrame(lignes_manquantes)
        genres = pd.concat([genres, df_manquants], ignore_index=True)

    # 6. RETOUR
    # On trie par ID pour insérer les parents potentiels (petits chiffres) avant les enfants souvent
    return genres.sort_values('genre_id').drop_duplicates(subset=['genre_id'])

def finaliser_liens_parents(df_complet, engine):
    df_liens = df_complet[['genre_id', 'genre_parent_id']].dropna().copy()
    df_liens['genre_id'] = df_liens['genre_id'].astype(int)
    df_liens['genre_parent_id'] = df_liens['genre_parent_id'].astype(int)
    
    if df_liens.empty:
        print("   Aucun lien parent à mettre à jour.")
        return

    df_liens.to_sql('temp_genre_update', engine, schema='sae', if_exists='replace', index=False)
    
    with engine.begin() as conn:
        sql_update = text("""
            UPDATE sae.genre AS g
            SET genre_parent_id = t.genre_parent_id
            FROM sae.temp_genre_update AS t
            WHERE g.genre_id = t.genre_id;
        """)
        conn.execute(sql_update)
        conn.execute(text("DROP TABLE sae.temp_genre_update;"))
    
def preparer_table_artists(df_source):
    # 1. SÉLECTION DES COLONNES SOURCE (Telles qu'elles sont dans le CSV)
    cols_source = [
        "artist_id", "artist_handle", "artist_name", "artist_bio",
        "artist_location", "artist_latitude", "artist_longitude",
        "artist_members", "artist_associated_labels", "artist_related_projects",
        "artist_active_year_begin", "artist_active_year_end", # Nom CSV
        "artist_contact", "artist_url", "artist_image_file"
    ]
    
    # On ne garde que ce qui existe vraiment
    cols_dispo = [c for c in cols_source if c in df_source.columns]
    artists = df_source[cols_dispo].copy()

    # 2. RENOMMAGE POUR COLLER AU SQL
    # C'est ici qu'on corrige l'erreur "UndefinedColumn"
    if 'artist_active_year_end' in artists.columns:
        artists = artists.rename(columns={'artist_active_year_end': 'artist_year_end'})

    # 3. NETTOYAGE ID
    artists['artist_id'] = pd.to_numeric(artists['artist_id'], errors='coerce')
    artists = artists.dropna(subset=['artist_id'])
    artists['artist_id'] = artists['artist_id'].astype(int)

    artists['artist_handle'] = artists['artist_handle'].fillna("").astype(str).str.strip().str.slice(0, 50)
    artists['artist_name'] = artists['artist_name'].fillna("").astype(str).str.strip().str.slice(0, 50)
    
    # B. Varchar(255)
    cols_255 = [
        "artist_location", "artist_members", "artist_associated_labels", 
        "artist_related_projects", "artist_contact", "artist_url", "artist_image_file"
    ]
    for col in cols_255:
        if col in artists.columns:
            artists[col] = artists[col].fillna("").astype(str).str.strip().str.slice(0, 255)

    # C. TEXT (Illimité)
    if "artist_bio" in artists.columns:
        artists['artist_bio'] = artists['artist_bio'].fillna("").astype(str).str.strip()

    # 5. NETTOYAGE NUMÉRIQUE
    # Coordonnées GPS
    for col in ["artist_latitude", "artist_longitude"]:
        if col in artists.columns:
            artists[col] = pd.to_numeric(artists[col], errors='coerce')

    # Années (Int)
    for col in ["artist_active_year_begin", "artist_year_end"]:
        if col in artists.columns:
            artists[col] = pd.to_numeric(artists[col], errors='coerce').astype('Int64')

    return artists

import pandas as pd

def preparer_table_albums(df_source):
    # 1. SÉLECTION DES COLONNES
    cols_source = [
        "album_id", "album_handle", "album_title", "album_information",
        "album_date_created", "album_date_released", 
        "album_producer", "album_engineer", 
        "album_image_file", "album_url",
        "album_type"  # Contient le texte (ex: "Live Performance")
    ]
    
    cols_dispo = [c for c in cols_source if c in df_source.columns]
    albums = df_source[cols_dispo].copy()

    # 2. NETTOYAGE ID ALBUM
    albums['album_id'] = pd.to_numeric(albums['album_id'], errors='coerce')
    albums = albums.dropna(subset=['album_id'])
    albums['album_id'] = albums['album_id'].astype(int)

    # ---------------------------------------------------------
    # 3. LE MAPPING (Texte -> ID)
    # ---------------------------------------------------------
    if 'album_type' in albums.columns:
        # A. On prépare le texte pour qu'il matche vos clés (minuscule, sans espaces)
        # fillna("") est important car vous avez la clé "" : 7
        clean_text = albums['album_type'].fillna("").astype(str).str.lower().str.strip()
        
        # B. On traduit grâce au dictionnaire
        albums['type_id'] = clean_text.map(map_album_type)
        
        # C. On convertit en format SQL (Int64 gère les NULLs si mapping échoue)
        albums['type_id'] = pd.to_numeric(albums['type_id'], errors='coerce').astype('Int64')
    else:
        albums['type_id'] = None

    # 4. GESTION DES DATES
    cols_dates = ["album_date_created", "album_date_released"]
    for col in cols_dates:
        if col in albums.columns:
            albums[col] = pd.to_datetime(albums[col], errors='coerce')

    # 5. NETTOYAGE TEXTES (Sécurité anti-crash)
    
    # Handle (50 chars max)
    if 'album_handle' in albums.columns:
        albums['album_handle'] = albums['album_handle'].fillna("").astype(str).str.strip().str.slice(0, 50)

    # Producer, Engineer (100 chars max)
    for col in ["album_producer", "album_engineer"]:
        if col in albums.columns:
            albums[col] = albums[col].fillna("").astype(str).str.strip().str.slice(0, 100)

    # Title, Image, Url (255 chars max)
    for col in ["album_title", "album_image_file", "album_url"]:
        if col in albums.columns:
            albums[col] = albums[col].fillna("").astype(str).str.strip().str.slice(0, 255)

    # Information (TEXT)
    if "album_information" in albums.columns:
        albums['album_information'] = albums['album_information'].fillna("").astype(str).str.strip()

    # 6. RETOUR (On renvoie type_id, pas album_type)
    cols_finales = [
        "album_id", "album_handle", "album_title", "album_information",
        "album_date_created", "album_date_released", 
        "album_producer", "album_engineer", 
        "album_image_file", "album_url",
        "type_id"
    ]
    
    # On filtre pour ne garder que ce qu'on a
    return albums[[c for c in cols_finales if c in albums.columns]]


def preparer_table_tracks(df_source):
    # 1. COPIE DE TRAVAIL
    tracks = df_source.copy()

    # 2. RENOMMAGE (Si la colonne s'appelle 'duration' au lieu de 'track_duration')
    if 'duration' in tracks.columns and 'track_duration' not in tracks.columns:
        tracks = tracks.rename(columns={'duration': 'track_duration'})

    # ---------------------------------------------------------
    # 3. CONVERSION DE LA DURÉE (LE FIX EST ICI)
    # ---------------------------------------------------------
    if 'track_duration' in tracks.columns:
        # On applique la fonction définie au-dessus sur toute la colonne
        tracks['track_duration'] = tracks['track_duration'].apply(convertir_duree)
    else:
        tracks['track_duration'] = None

    # 4. MAPPING LICENCE (Avec minuscules pour sécurité)
    if 'license_title' in tracks.columns:
        clean_license = tracks['license_title'].fillna("").astype(str).str.lower().str.strip()
        tracks['license_id'] = clean_license.map(map_license)
        tracks['license_id'] = pd.to_numeric(tracks['license_id'], errors='coerce').astype('Int64')
    else:
        tracks['license_id'] = None

    # 5. NETTOYAGE ID
    tracks['track_id'] = pd.to_numeric(tracks['track_id'], errors='coerce')
    tracks = tracks.dropna(subset=['track_id'])
    tracks['track_id'] = tracks['track_id'].astype(int)

    # 6. DATES
    for col in ["track_date_created", "track_date_recorded"]:
        if col in tracks.columns:
            tracks[col] = pd.to_datetime(tracks[col], errors='coerce')

    # 7. TRONCATURE TEXTES (Pour éviter le crash SQL)
    if 'track_title' in tracks.columns:
        tracks['track_title'] = tracks['track_title'].fillna("").astype(str).str.strip().str.slice(0, 255)

    for col in ["track_composer", "track_lyricist", "track_publisher"]:
        if col in tracks.columns:
            tracks[col] = tracks[col].fillna("").astype(str).str.strip().str.slice(0, 100)

    if 'track_file' in tracks.columns:
        # On utilise le domaine de stockage qui fonctionne
        base_url = "https://files.freemusicarchive.org/storage-freemusicarchive-org/"
        
        tracks['preview'] = tracks['track_file'].apply(
            lambda x: f"{base_url}{str(x).strip().lstrip('/')}" if pd.notna(x) and str(x).strip() != "" else None
        )
    else:
        tracks['preview'] = None
        
    # 8. AUTRES CHIFFRES
    if 'track_interest' in tracks.columns:
        tracks['track_interest'] = pd.to_numeric(tracks['track_interest'], errors='coerce')

    for col in ["track_listens", "track_favorites", "track_comments"]:
        if col in tracks.columns:
            tracks[col] = pd.to_numeric(tracks[col], errors='coerce').fillna(0).astype(int)
        else:
            tracks[col] = 0

    # 9. SÉLECTION FINALE
    cols_finales = [
        "track_id", "track_title", "track_duration", "preview",
        "track_listens", "track_favorites", "track_interest", "track_comments",
        "track_date_created", "track_date_recorded", 
        "track_composer", "track_lyricist", "track_publisher", 
        "license_id"
    ]
    
    # On comble les trous
    for col in cols_finales:
        if col not in tracks.columns:
            tracks[col] = None
            
    return tracks[cols_finales]

def preparer_liaison_ternaire(df_source, valid_tracks, valid_albums, valid_artists):
    cols = ["track_id", "album_id", "artist_id"]
    
    # Vérification des colonnes
    missing = [c for c in cols if c not in df_source.columns]
    if missing:
        print(f"❌ ERREUR: Colonnes manquantes dans le CSV : {missing}")
        return pd.DataFrame()

    df = df_source[cols].copy()

    # Nettoyage
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna().astype(int)

    # Filtrage Final
    df_final = df[
        df['track_id'].isin(valid_tracks) &
        df['album_id'].isin(valid_albums) &
        df['artist_id'].isin(valid_artists)
    ]
    
    return df_final.drop_duplicates()

def initialiser_stats_user(engine):    
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE sae.Stats_user CASCADE;"))
        
        sql = """
        INSERT INTO sae.Stats_user (
            user_id,
            danceability_affinity,
            energy_affinity,
            instrumentalness_affinity,
            liveness_affinity,
            speechness_affinity,
            tempo_affinity,
            valence_affinity,
            currency_affinity,
            hotness_affinity
        )
        SELECT 
            user_id,    -- On récupère l'ID de l'utilisateur
            0.0,        -- danceability
            0.0,        -- energy
            0.0,        -- instrumentalness
            0.0,        -- liveness
            0.0,        -- speechness
            0.0,        -- tempo
            0.0,        -- valence
            0.0,        -- currency
            0.0         -- hotness
        FROM sae.User;
        """
        conn.execute(text(sql))
        
def initialiser_search_history(engine):    
    with engine.begin() as conn:
        # 1. On vide la table par sécurité
        conn.execute(text("TRUNCATE TABLE sae.Search_History CASCADE;"))
        
        # 2. On insère une recherche par défaut pour chaque utilisateur
        # history_timestamp est automatique (DEFAULT CURRENT_TIMESTAMP)
        # history_id est automatique (SERIAL)
        sql = """
        INSERT INTO sae.Search_History (
            history_query,
            user_id
        )
        SELECT 
            'Bienvenue',  -- Texte de la recherche par défaut
            user_id       -- On récupère l'ID de chaque utilisateur
        FROM sae.User;
        """
        conn.execute(text(sql))

def preparer_stats_echonest(df_source, valid_track_ids):
    df = df_source.copy()

    # 1. GESTION DE L'ID (Header 2 crée souvent 'Unnamed: 0')
    if 'track_id' not in df.columns:
        # On prend la première colonne disponible comme ID
        col_0 = df.columns[0]
        df = df.rename(columns={col_0: 'track_id'})

    # Nettoyage ID
    df['track_id'] = pd.to_numeric(df['track_id'], errors='coerce')
    df = df.dropna(subset=['track_id'])
    df['track_id'] = df['track_id'].astype(int)

    # 2. FILTRAGE (On garde uniquement les tracks existants)
    df = df[df['track_id'].isin(valid_track_ids)]

    # =========================================================
    # 3. SÉLECTION PRÉCISE : SONG HOTNESS
    # =========================================================
    
    # ÉTAPE A : On supprime les colonnes ARTISTE qui polluent
    # C'est ça qui causait le bug : on vire artist_hotttnesss pour ne pas confondre
    cols_a_supprimer = [
        'artist_hotttnesss', 
        'artist_currency', 
        'artist_familiarity', 
        'artist_discovery'
    ]
    df = df.drop(columns=[c for c in cols_a_supprimer if c in df.columns], errors='ignore')

    # ÉTAPE B : On renomme les colonnes SONG vers les noms SQL
    # Ici, on force 'song_hotttnesss' à devenir 'hotness'
    mapping_cols = {
        'speechiness': 'speechness',
        'song_hotttnesss': 'hotness',  # <--- C'EST ICI QUE CA SE JOUE
        'song_currency': 'currency'
    }
    df = df.rename(columns=mapping_cols)

    # 4. SÉLECTION FINALE
    cols_cibles = [
        "track_id", 
        "acousticness", "danceability", "energy", "instrumentalness", 
        "liveness", "speechness", "tempo", "valence", 
        "currency", "hotness"
    ]
    
    # On ne garde que les colonnes qui existent
    cols_dispo = [c for c in cols_cibles if c in df.columns]
    df = df[cols_dispo].copy()

    # 5. NETTOYAGE DES TYPES
    for col in cols_dispo:
        if col != 'track_id':
            # Conversion numérique
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Cas particulier : Votre SQL attend des INT pour hotness/currency
            # Mais Echonest donne souvent des float (ex: 0.543).
            # Si on convertit 0.543 en int, ça fait 0.
            if col in ['currency', 'hotness']:
                # Optionnel : Si vos données sont entre 0 et 1, vous voudrez peut-être multiplier par 100 ?
                # Sinon, int(0.6) donne 0.
                # df[col] = (df[col] * 100).astype(int) # Décommentez si vous voulez un %
                df[col] = df[col].astype(int)

    return df.drop_duplicates(subset=['track_id'])

def preparer_track_genre(df_raw, existing_genre_ids):
    """
    Transforme la colonne 'track_genres' (liste de dicts en string) 
    en une table de liaison (track_id, genre_id).
    """
    
    # 1. On garde uniquement les colonnes utiles
    df = df_raw[['track_id', 'track_genres']].copy()
    
    # 2. Nettoyage initial : on retire les lignes vides
    df = df.dropna(subset=['track_genres'])
    
    # 3. Parsing : Convertir "[{'genre_id': '21', ...}]" en vraie liste Python
    # ast.literal_eval est plus sûr que eval()
    try:
        df['track_genres'] = df['track_genres'].apply(ast.literal_eval)
    except Exception as e:
        print(f"Erreur lors du parsing des genres : {e}")
        # En cas d'erreur, on peut retourner un DF vide ou filtrer
        return pd.DataFrame(columns=['track_id', 'genre_id'])

    # 4. Explode : On crée une ligne pour chaque genre d'une même track
    # Une track avec 3 genres deviendra 3 lignes
    df_exploded = df.explode('track_genres')
    
    # 5. On retire les NaN apparus si la liste était vide []
    df_exploded = df_exploded.dropna(subset=['track_genres'])
    
    # 6. Extraction de l'ID depuis le dictionnaire {'genre_id': '21', ...}
    # On suppose que chaque élément est un dict contenant 'genre_id'
    df_exploded['genre_id'] = df_exploded['track_genres'].apply(lambda x: int(x['genre_id']))
    
    # 7. Sélection finale
    df_final = df_exploded[['track_id', 'genre_id']].drop_duplicates()
    
    # 8. FILTRAGE DE SÉCURITÉ (Important !)
    # On ne garde que les genres qui existent VRAIMENT dans la table sae.Genre
    # Sinon, l'insertion plantera (Foreign Key Violation)
    df_final = df_final[df_final['genre_id'].isin(existing_genre_ids)]
    
    return df_final

def preparer_track_language(df_raw_tracks, engine):
    """
    Crée la liaison entre les Tracks et les Langues.
    Nécessite une connexion à la BDD pour récupérer les IDs des langues déjà insérées.
    """
    
    # 1. Récupérer le dictionnaire des langues depuis la BDD
    # On a besoin de savoir quel ID la base a donné à 'en', 'fr', etc.
    try:
        df_lang_db = pd.read_sql("SELECT language_id, language_name FROM sae.language", engine)
    except Exception as e:
        print(f"Erreur de lecture de la table Language : {e}")
        return pd.DataFrame()

    # On crée un dictionnaire : {'en': 1, 'fr': 2, 'es': 3 ...}
    map_languages = dict(zip(df_lang_db['language_name'], df_lang_db['language_id']))
    
    # 2. Préparer les données brutes
    # On suppose que la colonne dans le CSV s'appelle 'track_language_code' (standard FMA)
    # Si elle s'appelle autrement, adaptez le nom ici.
    col_langue_csv = 'track_language_code' 
    
    if col_langue_csv not in df_raw_tracks.columns:
        print(f"Attention : Colonne '{col_langue_csv}' introuvable dans le CSV.")
        return pd.DataFrame()

    df = df_raw_tracks[['track_id', col_langue_csv]].copy()
    
    # 3. Nettoyage
    df = df.dropna(subset=[col_langue_csv]) # On vire les tracks sans langue définie
    
    # 4. Mapping : On remplace le code 'en' par l'ID 1
    df['language_id'] = df[col_langue_csv].map(map_languages)
    
    # 5. Nettoyage final
    # Si une langue du CSV n'existe pas dans la table Language, map renvoie NaN. On supprime.
    df = df.dropna(subset=['language_id'])
    
    # Conversion en entier (car map peut transformer en float si NaN présent avant drop)
    df['language_id'] = df['language_id'].astype(int)
    
    # On ne garde que les colonnes utiles pour la table sql
    df_final = df[['track_id', 'language_id']]
    
    return df_final

def preparer_album_tag(df_raw_albums, engine):
    """
    Prépare la table de liaison Album_Tag.
    Nécessite de lire la table sae.Tag pour mapper les noms vers les IDs.
    """

    # 1. Récupération du dictionnaire des Tags depuis la BDD { 'rock': 1, 'pop': 2 ... }
    try:
        df_tags_db = pd.read_sql("SELECT tag_id, tag_name FROM sae.tag", engine)
    except Exception as e:
        print(f"Erreur lors de la lecture des tags en BDD : {e}")
        return pd.DataFrame()
    
    if df_tags_db.empty:
        print("Aucun tag trouvé en base. Impossible de lier les albums.")
        return pd.DataFrame()

    # On crée une map en minuscule pour éviter les soucis de casse (Rock vs rock)
    # { 'rock': 1, 'pop': 2 }
    map_tags = {str(name).lower(): id_ for name, id_ in zip(df_tags_db['tag_name'], df_tags_db['tag_id'])}

    # 2. Nettoyage du DataFrame source
    # Vérifiez le nom de la colonne dans votre CSV raw_albums.csv (souvent 'tags' ou 'album_tags')
    col_tags = 'tags' if 'tags' in df_raw_albums.columns else 'album_tags'
    
    if col_tags not in df_raw_albums.columns:
        print(f"Colonne des tags '{col_tags}' introuvable.")
        return pd.DataFrame()

    df = df_raw_albums[['album_id', col_tags]].dropna()

    # 3. Parsing de la liste (ex: "['rock', 'punk']")
    def safe_literal_eval(x):
        try:
            return ast.literal_eval(x)
        except:
            return []

    df[col_tags] = df[col_tags].apply(safe_literal_eval)

    # 4. Explode : On crée une ligne par tag
    df_exploded = df.explode(col_tags)
    df_exploded = df_exploded.dropna(subset=[col_tags])

    # 5. Mapping : On cherche l'ID correspondant au nom du tag
    # On met le tag du CSV en minuscule pour matcher la clé du dictionnaire
    df_exploded['tag_id'] = df_exploded[col_tags].apply(lambda x: map_tags.get(str(x).lower()))

    # 6. Nettoyage final : On vire les tags qui n'ont pas été trouvés dans la BDD
    df_final = df_exploded.dropna(subset=['tag_id']).copy()
    
    # Conversion en int
    # Maintenant df_final est indépendant, donc plus d'erreur ici
    df_final['tag_id'] = df_final['tag_id'].astype(int)

    # On renvoie uniquement les clés primaires composites
    return df_final[['album_id', 'tag_id']].drop_duplicates()

def preparer_track_tag(df_raw_tracks, engine):
    """
    Prépare la table de liaison Track_Tag.
    """
    print("--- Préparation de la liaison Track_Tag ---")

    # 1. Récupération des tags existants en BDD (mapping nom -> id)
    try:
        df_tags_db = pd.read_sql("SELECT tag_id, tag_name FROM sae.tag", engine)
    except Exception as e:
        print(f"Erreur lors de la lecture des tags en BDD : {e}")
        return pd.DataFrame()
    
    if df_tags_db.empty:
        return pd.DataFrame()

    # Map en minuscule { 'rock': 1, 'pop': 2 }
    map_tags = {str(name).lower(): id_ for name, id_ in zip(df_tags_db['tag_name'], df_tags_db['tag_id'])}

    # 2. Vérification de la colonne dans le CSV
    # Dans raw_tracks, c'est souvent 'tags'
    col_tags = 'tags'
    if col_tags not in df_raw_tracks.columns:
        print(f"Colonne '{col_tags}' introuvable dans raw_tracks.")
        return pd.DataFrame()

    # 3. Sélection et Nettoyage initial
    df = df_raw_tracks[['track_id', col_tags]].dropna()

    # Fonction pour transformer le string "['rock', 'jazz']" en liste Python
    def safe_literal_eval(x):
        try:
            return ast.literal_eval(x)
        except:
            return []

    df[col_tags] = df[col_tags].apply(safe_literal_eval)

    # 4. Explode (Une ligne par tag)
    df_exploded = df.explode(col_tags)
    df_exploded = df_exploded.dropna(subset=[col_tags])

    # 5. Mapping (Nom -> ID)
    df_exploded['tag_id'] = df_exploded[col_tags].apply(lambda x: map_tags.get(str(x).lower()))

    # 6. Nettoyage final + CORRECTION VIEW/COPY
    # On ajoute .copy() ici pour éviter le SettingWithCopyWarning
    df_final = df_exploded.dropna(subset=['tag_id']).copy()
    
    # 7. Conversion en int
    df_final['tag_id'] = df_final['tag_id'].astype(int)

    # 8. Retour (clés uniquement)
    return df_final[['track_id', 'tag_id']].drop_duplicates()

def preparer_artist_tag(df_raw_artists, engine):
    """
    Prépare la table de liaison Artist_Tag.
    """
    print("--- Préparation de la liaison Artist_Tag ---")

    # 1. Récupération des tags existants en BDD
    try:
        df_tags_db = pd.read_sql("SELECT tag_id, tag_name FROM sae.tag", engine)
    except Exception as e:
        print(f"Erreur lors de la lecture des tags en BDD : {e}")
        return pd.DataFrame()
    
    if df_tags_db.empty:
        return pd.DataFrame()

    # Map en minuscule pour la correspondance
    map_tags = {str(name).lower(): id_ for name, id_ in zip(df_tags_db['tag_name'], df_tags_db['tag_id'])}

    # 2. Vérification de la colonne
    col_tags = 'tags'
    if col_tags not in df_raw_artists.columns:
        print(f"Colonne '{col_tags}' introuvable dans raw_artists.")
        return pd.DataFrame()

    # 3. Sélection
    df = df_raw_artists[['artist_id', col_tags]].dropna()

    # 4. Parsing de la liste stringifiée "['rock', 'jazz']"
    def safe_literal_eval(x):
        try:
            return ast.literal_eval(x)
        except:
            return []

    df[col_tags] = df[col_tags].apply(safe_literal_eval)

    # 5. Explode (Une ligne par tag)
    df_exploded = df.explode(col_tags)
    df_exploded = df_exploded.dropna(subset=[col_tags])

    # 6. Mapping (Nom -> ID)
    df_exploded['tag_id'] = df_exploded[col_tags].apply(lambda x: map_tags.get(str(x).lower()))

    # 7. Nettoyage final + .COPY() (La solution au warning)
    df_final = df_exploded.dropna(subset=['tag_id']).copy()
    
    # 8. Typage et retour
    df_final['artist_id'] = df_final['artist_id'].astype(int)
    df_final['tag_id'] = df_final['tag_id'].astype(int)

    return df_final[['artist_id', 'tag_id']].drop_duplicates()

def preparer_artist_language(df_raw_tracks, engine):
    """
    Déduit la langue des artistes en se basant sur la langue de leurs tracks.
    (Source : df_raw_tracks)
    """
    print("--- Préparation de la liaison Artist_Language (via Tracks) ---")

    # ==============================================================================
    # 1. ÉTAPE DE SÉCURITÉ : Récupérer les ID des artistes qui existent VRAIMENT
    # ==============================================================================
    try:
        df_valid_artists = pd.read_sql("SELECT artist_id FROM sae.artist", engine)
        valid_artist_ids = set(df_valid_artists['artist_id']) # On fait un set pour la rapidité
    except Exception as e:
        print(f"Erreur lecture Artist BDD : {e}")
        return pd.DataFrame()
    
    # 2. Récupération des langues en BDD
    try:
        df_lang_db = pd.read_sql("SELECT language_id, language_name FROM sae.language", engine)
    except Exception as e:
        print(f"Erreur lecture Language : {e}")
        return pd.DataFrame()

    if df_lang_db.empty:
        return pd.DataFrame()

    # Dictionnaire : {'en': 1, 'fr': 2 ...}
    map_languages = dict(zip(df_lang_db['language_name'], df_lang_db['language_id']))

    # 3. Colonnes nécessaires
    col_lang = 'track_language_code'
    if col_lang not in df_raw_tracks.columns or 'artist_id' not in df_raw_tracks.columns:
        return pd.DataFrame()

    # 4. Sélection
    df = df_raw_tracks[['artist_id', col_lang]].copy()
    df = df.dropna()

    # 5. Mapping Langue
    df['language_id'] = df[col_lang].map(map_languages)
    df = df.dropna(subset=['language_id'])

    # 6. Typage
    df['artist_id'] = pd.to_numeric(df['artist_id'], errors='coerce').fillna(0).astype(int)
    df['language_id'] = df['language_id'].astype(int)

    # ==============================================================================
    # 7. FILTRAGE CRITIQUE : On ne garde que les artistes connus
    # ==============================================================================
    # C'est cette ligne qui corrige ton erreur ForeignKeyViolation
    df_final = df[df['artist_id'].isin(valid_artist_ids)].copy()

    # 8. DEDUPLICATION
    return df_final[['artist_id', 'language_id']].drop_duplicates()

def preparer_track_genre_majoritaire(df_raw_tracks, engine):
    """
    Prépare la table de liaison Track_Genre_Majoritaire.
    VERSION AVANCÉE : Utilise la liste 'track_genres' JSON car 'track_genre_top' est absente.
    On cherche en priorité un genre 'Racine' (sans parent).
    """
    print("--- Préparation de la liaison Track_Genre_Majoritaire (via JSON) ---")

    # 1. On récupère les IDs des genres "Racines" (ceux qui n'ont pas de parent)
    # Ce sont les "Majoritaires" par définition (Rock, Pop, Electronic...)
    try:
        query = "SELECT genre_id FROM sae.genre WHERE genre_parent_id IS NULL"
        df_roots = pd.read_sql(query, engine)
        root_ids = set(df_roots['genre_id']) # Set pour recherche rapide (ex: {21, 10, 38...})
    except Exception as e:
        print(f"Erreur lecture des genres racines : {e}")
        # Si erreur, on fera sans la priorité
        root_ids = set()

    # 2. Vérification de la colonne JSON
    col_json = 'track_genres'
    if col_json not in df_raw_tracks.columns:
        print(f"Colonne '{col_json}' absente. Impossible de déduire le genre majoritaire.")
        return pd.DataFrame()

    # 3. Sélection et Parsing
    df = df_raw_tracks[['track_id', col_json]].copy()
    df = df.dropna(subset=[col_json])

    def extraire_majoritaire(chaine_json):
        try:
            liste_genres = ast.literal_eval(chaine_json)
            if not isinstance(liste_genres, list) or not liste_genres:
                return None
            
            # On récupère tous les IDs de cette track
            ids_du_track = [int(g['genre_id']) for g in liste_genres if 'genre_id' in g]
            
            if not ids_du_track:
                return None

            # STRATÉGIE :
            # A. Y a-t-il un ID qui fait partie des genres Racines (Roots) ?
            for genre_id in ids_du_track:
                if genre_id in root_ids:
                    return genre_id # On a trouvé un chef (ex: Hip-Hop)
            
            # B. Sinon, on prend le tout premier de la liste par défaut
            return ids_du_track[0]

        except:
            return None

    # 4. Application de la logique
    df['genre_id'] = df[col_json].apply(extraire_majoritaire)

    # 5. Nettoyage
    df_final = df.dropna(subset=['genre_id']).copy()
    
    # 6. Typage
    df_final['track_id'] = df_final['track_id'].astype(int)
    df_final['genre_id'] = df_final['genre_id'].astype(int)

    # 7. SÉCURITÉ : On vérifie que le genre choisi existe vraiment dans la table Genre
    # (Pour éviter l'erreur ForeignKeyViolation)
    try:
        all_genre_ids = set(pd.read_sql("SELECT genre_id FROM sae.genre", engine)['genre_id'])
        df_final = df_final[df_final['genre_id'].isin(all_genre_ids)]
    except:
        pass

    return df_final[['track_id', 'genre_id']].drop_duplicates()

def preparer_score_period(df_questionnaire, engine):
    """
    Lie les utilisateurs aux périodes qu'ils préfèrent (via le questionnaire).
    Source : df_questionnaire
    Cible : Table de liaison (user_id, period_id)
    """
    print("--- Préparation de Score_Period (Préférences Utilisateurs) ---")

    # 1. Récupérer les périodes de la BDD
    try:
        df_periods_db = pd.read_sql("SELECT period_id, period_interval FROM sae.period", engine)
    except:
        return pd.DataFrame()

    if df_periods_db.empty:
        return pd.DataFrame()

    # 2. Préparer le DataFrame Utilisateur
    # IMPORTANT : On recrée les user_id comme dans 'preparer_table_users'
    # On suppose que la ligne 0 du CSV = user_id 1, ligne 1 = user_id 2, etc.
    df = df_questionnaire.copy()
    df['user_id'] = range(1, len(df) + 1)

    # 3. Identifier la colonne du questionnaire
    # Cherche une colonne qui parle de "période", "année" ou "décennie"
    col_target = None
    cols_possibles = ["Quelle décennie vous attire le plus ?", "période", "année", "décennie"]
    
    for col in df.columns:
        if any(keyword in col.lower() for keyword in cols_possibles):
            col_target = col
            break
    
    if not col_target:
        print("   -> Colonne 'Période' introuvable dans le questionnaire.")
        # On renvoie un DF vide ou on met une valeur par défaut ?
        return pd.DataFrame()

    # 4. Logique de Mapping (Réponse Utilisateur -> ID Période)
    # Ex: Utilisateur répond "Années 80" -> On cherche "1980 - 1990"
    def trouver_id_periode(reponse_user):
        reponse_str = str(reponse_user)
        for _, row in df_periods_db.iterrows():
            intervalle = str(row['period_interval'])
            # Si l'intervalle (ex: "1990") est dans la réponse (ex: "Années 1990")
            # Ou inversement, ou correspondance simple sur les 3 premiers chiffres (ex: "199")
            if intervalle[:3] in reponse_str: 
                return row['period_id']
        # Fallback : Si on ne trouve rien, on met peut-être la période la plus récente ou rien
        return None

    df['period_id'] = df[col_target].apply(trouver_id_periode)

    # 5. Nettoyage
    df_final = df.dropna(subset=['period_id']).copy()
    df_final['user_id'] = df_final['user_id'].astype(int)
    df_final['period_id'] = df_final['period_id'].astype(int)

    return df_final[['user_id', 'period_id']].drop_duplicates()

def preparer_score_mood(df_questionnaire, engine):
    """
    Lie les utilisateurs aux moods qu'ils recherchent.
    Source : df_questionnaire
    """
    print("--- Préparation de Score_Mood (Préférences Utilisateurs) ---")

    # 1. Récupérer les Moods de la BDD
    try:
        df_moods_db = pd.read_sql("SELECT mood_id, mood_name FROM sae.mood", engine)
    except:
        return pd.DataFrame()

    # Mapping { "happy": 1, "joyeux": 1 ... }
    # On prépare un dictionnaire intelligent pour comprendre le français
    map_bdd = {str(n).lower().strip(): i for n, i in zip(df_moods_db['mood_name'], df_moods_db['mood_id'])}
    
    # Alias pour comprendre les réponses du questionnaire (adapter selon vos questions)
    # Clé = Mot clé dans le questionnaire / Valeur = Nom dans la BDD (en anglais souvent)
    alias_francais = {
        "joyeux": "happy", "heureux": "happy", "fête": "happy",
        "triste": "sad", "mélancolique": "sad", "deprime": "sad",
        "calme": "calm", "détente": "calm", "repos": "calm",
        "énervé": "angry", "colère": "angry", "sport": "angry" # Sport est souvent associé à l'énergie/colère
    }

    # 2. Préparer Utilisateur
    df = df_questionnaire.copy()
    df['user_id'] = range(1, len(df) + 1)

    # 3. Identifier la colonne "Ambiance"
    col_target = None
    cols_possibles = ["ambiance", "humeur", "mood", "comment vous sentez-vous"]
    
    for col in df.columns:
        if any(keyword in col.lower() for keyword in cols_possibles):
            col_target = col
            break
            
    if not col_target:
        print("   -> Colonne 'Mood/Ambiance' introuvable dans le questionnaire.")
        return pd.DataFrame()

    # 4. Mapping
    def trouver_id_mood(reponse_user):
        txt = str(reponse_user).lower()
        
        # A. Recherche via Alias Français
        mood_anglais = None
        for mot_cle, traduction in alias_francais.items():
            if mot_cle in txt:
                mood_anglais = traduction
                break
        
        # Si on n'a pas trouvé d'alias, on suppose que c'est peut-être déjà en anglais
        if not mood_anglais:
            mood_anglais = txt

        # B. Recherche ID dans la map BDD
        # On cherche correspondance exacte ou partielle
        for db_name, db_id in map_bdd.items():
            if db_name in mood_anglais or mood_anglais in db_name:
                return db_id
                
        return None

    df['mood_id'] = df[col_target].apply(trouver_id_mood)

    # 5. Nettoyage
    df_final = df.dropna(subset=['mood_id']).copy()
    df_final['user_id'] = df_final['user_id'].astype(int)
    df_final['mood_id'] = df_final['mood_id'].astype(int)

    return df_final[['user_id', 'mood_id']].drop_duplicates()

def preparer_user_context(df_questionnaire, engine):
    """
    Lie les utilisateurs aux contextes d'écoute (Sport, Travail, etc.).
    Table : sae.User_Context
    """
    print("--- Préparation de la liaison User_Context ---")

    # 1. Récupérer les ID et Noms depuis la BDD
    try:
        df_db = pd.read_sql("SELECT context_id, context_name FROM sae.context", engine)
    except:
        return pd.DataFrame()

    if df_db.empty:
        return pd.DataFrame()

    # Dictionnaire { "sport": 1, "travail": 2 ... } (tout en minuscule)
    map_context = {str(n).lower().strip(): i for n, i in zip(df_db['context_name'], df_db['context_id'])}

    # 2. Préparer le DataFrame User
    # On recrée les ID basés sur l'ordre (comme dans preparer_table_users)
    df = df_questionnaire.copy()
    df['user_id'] = range(1, len(df) + 1)

    # 3. Trouver la colonne "Contexte" dans le CSV
    col_target = None
    keywords = ["contexte", "situation", "moment", "activité"]
    for col in df.columns:
        if any(k in col.lower() for k in keywords):
            col_target = col
            break
    
    if not col_target:
        print("   -> Colonne 'Contexte' introuvable dans le questionnaire.")
        return pd.DataFrame()

    # 4. Fonction de détection de mots-clés
    # Si la réponse est "Je fais du sport", on trouve "sport".
    def detecter_ids(reponse_txt):
        txt = str(reponse_txt).lower()
        ids_trouves = []
        for context_name, context_id in map_context.items():
            # On cherche si le nom du contexte (ex: "sport") est dans la phrase de l'user
            if context_name in txt:
                ids_trouves.append(context_id)
        return ids_trouves

    # On applique la détection
    df['found_ids'] = df[col_target].apply(detecter_ids)

    # 5. Explode (car un user peut avoir plusieurs contextes)
    df_exploded = df.explode('found_ids')
    
    # 6. Nettoyage
    df_final = df_exploded.dropna(subset=['found_ids']).copy()
    df_final = df_final.rename(columns={'found_ids': 'context_id'})
    
    df_final['user_id'] = df_final['user_id'].astype(int)
    df_final['context_id'] = df_final['context_id'].astype(int)

    return df_final[['user_id', 'context_id']].drop_duplicates()


def preparer_user_platform(df_questionnaire, engine):
    """
    Lie les utilisateurs aux plateformes.
    CORRECTION : Force la colonne exacte pour éviter de prendre les genres.
    """
    print("--- Préparation de la liaison User_Platform ---")

    # 1. BDD
    try:
        df_db = pd.read_sql("SELECT platform_id, platform_name FROM sae.platform", engine)
    except:
        return pd.DataFrame()

    if df_db.empty:
        return pd.DataFrame()

    map_platform = {str(n).lower().strip(): i for n, i in zip(df_db['platform_name'], df_db['platform_id'])}
    
    # 2. User
    df = df_questionnaire.copy()
    df['user_id'] = range(1, len(df) + 1)

    # 3. SÉLECTION DE LA COLONNE (C'est ici qu'on corrige)
    col_target = None
    
    # Nom exact fourni dans ton CSV
    nom_exact = "Sur quelle plateforme écoutez vous de la musique ?"
    
    if nom_exact in df.columns:
        col_target = nom_exact
    else:
        # Fallback de sécurité si jamais il y a un espace en plus ou en moins
        for col in df.columns:
            # On cherche "plateforme" MAIS on exclut "genre" pour ne pas se tromper
            if "plateforme" in col.lower() and "genre" not in col.lower():
                col_target = col
                break

    if not col_target:
        print(f"   -> ERREUR CRITIQUE : Colonne '{nom_exact}' introuvable.")
        print(f"   -> Colonnes dispos : {df.columns.tolist()}")
        return pd.DataFrame()

    # 4. ALIAS (Ton mapping personnalisé)
    alias = {
        "apple": "applemusic", "iphone": "applemusic",
        "youtube": "youtube", "yt": "youtube",
        "spotify": "spotify", "deezer": "deezer", "soundcloud": "soundcloud",
        "télécharg": "téléchargée", "dl": "téléchargée", "mp3": "téléchargée",
        "fichiers": "téléchargée", "files": "téléchargée", "usb": "téléchargée",
        "cd": "cd", "disque": "cd", "physique": "cd", "vinyle": "cd",
        "amazon": "amazon music",
        "amerigo": "amerigo", "nintendo": "nintendo music", "free": "freemusic",
        "radio": "radio", "tv": "tv", "télé": "tv"
    }

    def detecter_ids(reponse_txt):
        if pd.isna(reponse_txt): return []
        txt = str(reponse_txt).lower()
        ids_trouves = []
        
        for mot_cle_csv, target_bdd_name in alias.items():
            if mot_cle_csv in txt:
                if target_bdd_name in map_platform:
                    ids_trouves.append(map_platform[target_bdd_name])

        for db_name, db_id in map_platform.items():
            if db_name in txt and db_id not in ids_trouves:
                ids_trouves.append(db_id)
                
        return list(set(ids_trouves))

    # 5. Application
    df['found_ids'] = df[col_target].apply(detecter_ids)
    df_exploded = df.explode('found_ids')
    df_final = df_exploded.dropna(subset=['found_ids']).copy()
    
    if df_final.empty:
        print("   -> DEBUG : Toujours vide. Voici les réponses de la colonne ciblée :")
        print(df[col_target].head(5).tolist())

    df_final = df_final.rename(columns={'found_ids': 'platform_id'})
    df_final['user_id'] = df_final['user_id'].astype(int)
    df_final['platform_id'] = df_final['platform_id'].astype(int)

    return df_final[['user_id', 'platform_id']].drop_duplicates()


def preparer_user_languages(df_sondage):
    """
    Crée la table de liaison User_Language en utilisant les maps du fichier map.py.
    
    :param df_sondage: DataFrame du questionnaire
    :param df_ref_languages: (Optionnel ici car on utilise map_langue_iso directement)
    """
    print("Création de la relation User <-> Language...")
    
    col_langue_sondage = "Langue(s) écoutée(s)"
    
    if col_langue_sondage not in df_sondage.columns:
        print(f"Attention: Colonne '{col_langue_sondage}' introuvable.")
        return pd.DataFrame(columns=['user_id', 'language_id'])

    data_liaison = []
    
    # On parcourt le sondage
    for index, row in df_sondage.iterrows():
        # L'user_id commence à 1
        user_id = index + 1
        
        # Récupération de la réponse (ex: "Français, Anglais")
        reponse_langues = str(row[col_langue_sondage])
        
        if pd.isna(reponse_langues) or reponse_langues.lower() == 'nan':
            continue
            
        # Découpage
        # On sépare par virgule et on nettoie les espaces
        liste_noms = [l.strip() for l in reponse_langues.split(',')]
        
        for nom_langue in liste_noms:
            # 1. Conversion Nom Sondage -> Code ISO (via map_langue_to_iso)
            # Ex: "Français" -> "fr"
            code_iso = map_langue_to_iso.get(nom_langue)
            
            if code_iso:
                # 2. Conversion Code ISO -> ID BDD (via map_langue_iso)
                # Ex: "fr" -> 14
                lang_id = map_langue_iso.get(code_iso)
                
                if lang_id:
                    data_liaison.append({
                        'user_id': user_id,
                        'language_id': lang_id
                    })
                else:
                    # Le code ISO existe mais n'est pas dans la map des IDs (peut-être pas de tracks avec cette langue)
                    pass
            else:
                # La langue du sondage n'est pas dans map_langue_to_iso (ex: une typo ou nouvelle langue)
                # On peut essayer de voir si c'est directement un code ou gérer des cas particuliers ici
                pass

    # Création du DataFrame final
    df_user_lang = pd.DataFrame(data_liaison)
    
    # Suppression des doublons (au cas où un user répète une langue)
    if not df_user_lang.empty:
        df_user_lang = df_user_lang.drop_duplicates()
        
    return df_user_lang

def preparer_genre_top_user(df_questionnaire, engine):
    print(">>> Préparation de la table : genre_top_user (Version Finale)...")

    # 1. Chargement des genres BDD
    query = "SELECT genre_id, genre_title FROM sae.genre"
    df_db_genres = pd.read_sql(query, engine)
    map_genre_db = dict(zip(df_db_genres['genre_title'].str.lower().str.strip(), df_db_genres['genre_id']))

    # Nom exact de la colonne dans ton CSV
    colonne_csv = "Quels genres écoutez-vous le plus ?"

    data_rows = []

    for idx, row in df_questionnaire.iterrows():
        # On suppose que l'ID suit l'ordre d'insertion (1, 2, 3...)
        user_id = idx + 1 

        if colonne_csv in row and pd.notna(row[colonne_csv]):
            chaine_genres = str(row[colonne_csv])
            
            # --- CORRECTION ICI ---
            # On remplace les '/' par des ',' pour séparer "Electro / Techno"
            chaine_genres = chaine_genres.replace('/', ',')
            
            # On découpe
            liste_genres = chaine_genres.split(',')
            
            current_score = 10.0

            for genre_brut in liste_genres:
                genre_clean = genre_brut.lower().strip()
                
                # On ignore les chaines vides
                if not genre_clean: continue

                # Recherche ID
                genre_id = map_genre_db.get(genre_clean)

                # Fuzzy Search rapide
                if not genre_id:
                    for db_name, db_id in map_genre_db.items():
                        if genre_clean in db_name or db_name in genre_clean:
                            genre_id = db_id
                            break
                
                if genre_id:
                    data_rows.append({
                        'user_id': int(user_id),
                        'genre_id': int(genre_id),
                        'genre_rate': float(current_score)
                    })
                    # Décroissance du score
                    current_score = max(2.0, current_score - 2.0)

    df_result = pd.DataFrame(data_rows)
    
    if not df_result.empty:
        df_result = df_result.drop_duplicates(subset=['user_id', 'genre_id'])
        print(f">>> Succès : {len(df_result)} préférences musicales chargées.")
    else:
        print(">>> ATTENTION : Aucun genre extrait.")
        df_result = pd.DataFrame(columns=['user_id', 'genre_id', 'genre_rate'])

    return df_result