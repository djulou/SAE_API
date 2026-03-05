import pandas as pd
import requests
import os
import io
import sys
import time
import csv  # <--- IMPORT CRUCIAL
import cleaning
from sqlalchemy import create_engine, text
from fonction import clean_csv
from map import map_mood, map_contexte, map_platforme, map_periode

# --- 1. CONFIGURATION ---
if os.path.exists("/app/data"):
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/mabase")
    base_dir = "/app/data"
    sql_path = "/app/init.sql"
    print(">>> Environnement : Docker détecté.")
else:
    DATABASE_URL = "postgresql://user:password@localhost:5433/mabase"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.join(script_dir, "../data/")
    sql_path = os.path.join(script_dir, "../init.sql")
    print(f">>> Environnement : Local détecté.")

engine = create_engine(DATABASE_URL)
BASE_URL = "https://api.deezer.com"

# --- 2. ATTENTE CONNEXION ---
connected = False
while not connected:
    try:
        with engine.connect() as conn:
            connected = True
            print(">>> Connecté à Postgres.")
    except:
        time.sleep(1)

# --- 3. FONCTIONS ---

def is_db_populated(engine):
    from sqlalchemy import inspect
    inspector = inspect(engine)
    # On vérifie si la table "User" existe et si elle a des lignes
    if "user" in inspector.get_table_names(schema="sae"):
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sae.user"))
            count = result.scalar()
            return count > 0
    return False

def psql_insert_copy(table, conn, keys, data_iter):
    """
    Version BLINDÉE utilisant csv.writer.
    Gère les caractères spéciaux, les guillemets et les délimiteurs.
    """
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = io.StringIO()
        # On utilise le module CSV pour écrire proprement (gère les quotes automatiquement)
        writer = csv.writer(s_buf, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
        
        for row in data_iter:
            cleaned_row = []
            for val in row:
                if val is None:
                    cleaned_row.append('')
                else:
                    # On nettoie quand même les retours à la ligne excessifs pour la propreté
                    str_val = str(val).replace('\n', ' ').replace('\r', '')
                    cleaned_row.append(str_val)
            writer.writerow(cleaned_row)
            
        s_buf.seek(0)

        # Gestion des schémas et noms de tables (avec guillemets pour "user")
        if table.schema:
            full_table_name = f'"{table.schema}"."{table.name}"'
        else:
            full_table_name = f'"{table.name}"'

        columns_list = ', '.join([f'"{k}"' for k in keys])
        
        # On précise FORMAT CSV pour que Postgres utilise le parser CSV robuste
        sql_query = f"COPY {full_table_name} ({columns_list}) FROM STDIN WITH (FORMAT CSV, DELIMITER '\t', NULL '')"

        try:
            cur.copy_expert(sql_query, s_buf)
        except Exception as e:
            print(f"❌ Erreur COPY sur {full_table_name}: {e}")
            raise e

def fetch_api(endpoint, params=None):
    try:
        res = requests.get(f"{BASE_URL}/{endpoint}", params=params)
        if res.status_code == 200: return res.json()
    except Exception as e:
        print(f"Erreur API {endpoint}: {e}")
    return None

def mass_populate(engine, dict_dfs):
    with engine.begin() as conn:
        conn.execute(text("SET session_replication_role = 'replica';"))
        try:
            for table_name, df in dict_dfs.items():
                if df is not None and not df.empty:
                    print(f"📥 Insertion Deezer (COPY) -> {table_name}...")
                    df.to_sql(table_name, conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            print("🔄 Rafraîchissement Vue Matérialisée...")
            conn.execute(text("REFRESH MATERIALIZED VIEW sae.View_Track_Materialise;"))
        finally:
            conn.execute(text("SET session_replication_role = 'origin';"))

def harvest_everything(limit_count=20):
    print(f"🚀 Collecte Deezer (Limite: {limit_count})...")
    artists, albums, tracks, links = [], [], [], []
    seen_art, seen_alb = set(), set()

    genres_data = fetch_api("genre")
    if not genres_data: return

    for genre in genres_data.get('data', [])[:limit_count]:
        if genre['name'].lower() == "all": continue
        
        arts = fetch_api(f"genre/{genre['id']}/artists")
        if not arts: continue

        for art in arts.get('data', [])[:limit_count]:
            if art['id'] not in seen_art:
                artists.append({
                    "artist_id": art['id'], "artist_name": art['name'],
                    "artist_handle": f"art-{art['id']}", "artist_image_file": art['picture_medium']
                })
                seen_art.add(art['id'])

            albs = fetch_api(f"artist/{art['id']}/albums")
            if not albs: continue

            for alb in albs.get('data', [])[:limit_count]:
                if alb['id'] not in seen_alb:
                    albums.append({
                        "album_id": alb['id'], "album_title": alb['title'],
                        "album_handle": f"alb-{alb['id']}", "album_image_file": alb.get('cover_medium'),
                        "album_date_released": alb.get('release_date', '2020-01-01')
                    })
                    seen_alb.add(alb['id'])

                trks = fetch_api(f"album/{alb['id']}/tracks")
                if not trks: continue
                for trk in trks.get('data', []):
                    # We append everything; deduplication happens later
                    tracks.append({
                        "track_id": trk['id'], "track_title": trk['title'],
                        "track_duration": trk['duration'], "preview": trk.get('preview')
                    })
                    links.append({"artist_id": art['id'], "album_id": alb['id'], "track_id": trk['id']})
            time.sleep(0.05)

    # --- DEDUPLICATION PHASE ---
    print("🧹 Nettoyage et Déduplication des données Deezer...")
    
    df_artist = pd.DataFrame(artists)
    df_album = pd.DataFrame(albums)
    df_track = pd.DataFrame(tracks)
    df_links = pd.DataFrame(links)

    # 1. Deduplicate the new data itself (API often returns duplicates)
    if not df_artist.empty: df_artist.drop_duplicates(subset=['artist_id'], keep='first', inplace=True)
    if not df_album.empty: df_album.drop_duplicates(subset=['album_id'], keep='first', inplace=True)
    if not df_track.empty: df_track.drop_duplicates(subset=['track_id'], keep='first', inplace=True)
    if not df_links.empty: df_links.drop_duplicates(subset=['artist_id', 'album_id', 'track_id'], keep='first', inplace=True)

    # 2. Type Conversion (Float -> Int) safety check
    for df in [df_artist, df_album, df_track, df_links]:
        if not df.empty and "track_id" in df.columns:
             df["track_id"] = pd.to_numeric(df["track_id"], errors='coerce').fillna(0).astype(int)
        if not df.empty and "album_id" in df.columns:
             df["album_id"] = pd.to_numeric(df["album_id"], errors='coerce').fillna(0).astype(int)
        if not df.empty and "artist_id" in df.columns:
             df["artist_id"] = pd.to_numeric(df["artist_id"], errors='coerce').fillna(0).astype(int)

    # 3. FILTER AGAINST DB: Remove items that already exist (from CSVs)
    try:
        print("🔍 Checking against existing DB entries to avoid conflicts...")
        with engine.connect() as conn:
            existing_tracks = set(pd.read_sql("SELECT track_id FROM sae.track", conn)["track_id"])
            existing_albums = set(pd.read_sql("SELECT album_id FROM sae.album", conn)["album_id"])
            existing_artists = set(pd.read_sql("SELECT artist_id FROM sae.artist", conn)["artist_id"])

        if not df_track.empty:
            # Only keep tracks that are NOT in the database
            df_track = df_track[~df_track['track_id'].isin(existing_tracks)]
            print(f"   -> {len(df_track)} new tracks to insert.")
            
        if not df_album.empty:
            df_album = df_album[~df_album['album_id'].isin(existing_albums)]
            
        if not df_artist.empty:
            df_artist = df_artist[~df_artist['artist_id'].isin(existing_artists)]
            
    except Exception as e:
        print(f"⚠️ Warning during DB check: {e}")

    dfs = {
        "artist": df_artist,
        "album": df_album,
        "track": df_track,
        "artist_album_track": df_links
    }

    mass_populate(engine, dfs)

# --- 4. MAIN ---

def main():
    # ÉTAPE 0 : INIT SQL
    if is_db_populated(engine):
        print("✅ La base de données est déjà peuplée. Saut de l'étape d'importation.")
        sys.exit(0) # On sort proprement
    else:
        print("🧹 [ÉTAPE 0] Initialisation SQL...")
        with engine.begin() as conn:
            if os.path.exists(sql_path):
                with open(sql_path, "r", encoding="utf-8") as f:
                    conn.execute(text(f.read()))
                print("✅ Tables recréées.")
            else:
                print(f"⚠️ ERREUR : {sql_path} introuvable.")
                return

        # ÉTAPE 1 : LECTURE CSV
        print("📂 [ÉTAPE 1] Lecture CSV...")
        df_questionnaire = pd.read_csv(os.path.join(base_dir, "questionnaire.csv"))
        df_raw_tracks = pd.read_csv(os.path.join(base_dir, "raw_tracks.csv"))
        df_raw_albums = pd.read_csv(os.path.join(base_dir, "raw_albums.csv"))
        df_raw_artists = pd.read_csv(os.path.join(base_dir, "raw_artists.csv"))
        df_raw_genres = pd.read_csv(os.path.join(base_dir, "raw_genres.csv"))
        df_raw_echonest = pd.read_csv(os.path.join(base_dir, "raw_echonest.csv"), header=2, on_bad_lines="skip")

        # Préparation
        df_users = cleaning.preparer_table_users(df_questionnaire)
        df_licenses = cleaning.preparer_table_licenses(df_raw_tracks)
        df_types = cleaning.preparer_table_album_type(df_raw_albums)
        df_languages = cleaning.preparer_table_languages(df_raw_tracks)
        df_tags = cleaning.preparer_table_tags_globale(df_raw_tracks, df_raw_albums, df_raw_artists)
        
        df_genres_pret = cleaning.preparer_table_genres(df_raw_genres)
        df_pour_insertion_genre = df_genres_pret.copy()
        df_pour_insertion_genre["genre_parent_id"] = None
        
        df_artist = cleaning.preparer_table_artists(clean_csv(df_raw_artists))
        df_album = cleaning.preparer_table_albums(clean_csv(df_raw_albums))
        df_track = cleaning.preparer_table_tracks(df_raw_tracks)
        
        # Mapping
        df_mood = pd.DataFrame(list(map_mood.items()), columns=["mood_name", "mood_id"])
        df_contexte = pd.DataFrame(list(map_contexte.items()), columns=["context_name", "context_id"])
        df_platform = pd.DataFrame(list(map_platforme.items()), columns=["platform_name", "platform_id"])
        df_period = pd.DataFrame(list(map_periode.items()), columns=["period_interval", "period_id"])

        # CONVERSION DES TYPES (Float -> Int)
        print("🔧 Correction des types...")
        try:
            df_languages["language_id"] = pd.to_numeric(df_languages["language_id"], errors='coerce').fillna(0).astype(int)
            df_licenses["license_id"] = pd.to_numeric(df_licenses["license_id"], errors='coerce').fillna(0).astype(int)
            df_types["type_id"] = pd.to_numeric(df_types["type_id"], errors='coerce').fillna(0).astype(int)
            df_tags["tag_id"] = pd.to_numeric(df_tags["tag_id"], errors='coerce').fillna(0).astype(int)
            df_pour_insertion_genre["genre_id"] = pd.to_numeric(df_pour_insertion_genre["genre_id"], errors='coerce').fillna(0).astype(int)
            df_artist["artist_id"] = pd.to_numeric(df_artist["artist_id"], errors='coerce').fillna(0).astype(int)
            df_album["album_id"] = pd.to_numeric(df_album["album_id"], errors='coerce').fillna(0).astype(int)
            df_track["track_id"] = pd.to_numeric(df_track["track_id"], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            print(f"⚠️ Attention types : {e}")

        # ÉTAPE 2 : INSERTION CSV (Via COPY csv.writer)
        print("📥 [ÉTAPE 2] Insertion CSV...")
        with engine.begin() as conn:
            # Ref
            df_users.to_sql("user", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_mood.to_sql("mood", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_contexte.to_sql("context", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_platform.to_sql("platform", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_period.to_sql("period", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            
            # Meta Musique
            df_types.to_sql("album_type", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_licenses.to_sql("license", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_languages.to_sql("language", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_tags.to_sql("tag", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            df_pour_insertion_genre.to_sql("genre", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            
            # Musique Core
            print("   -> Insertion Artistes (Cela peut prendre un moment)...")
            df_artist.to_sql("artist", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            print("   -> Insertion Albums...")
            df_album.to_sql("album", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)
            print("   -> Insertion Tracks...")
            df_track.to_sql("track", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)

        cleaning.initialiser_stats_user(engine)
        cleaning.initialiser_search_history(engine)
        cleaning.finaliser_liens_parents(df_genres_pret, engine)

        # Liaisons (to_sql standard ou copy selon besoin)
        ids_tracks = set(pd.read_sql("SELECT track_id FROM sae.track", engine)["track_id"])
        ids_albums = set(pd.read_sql("SELECT album_id FROM sae.album", engine)["album_id"])
        ids_artists = set(pd.read_sql("SELECT artist_id FROM sae.artist", engine)["artist_id"])
        ids_genres = set(pd.read_sql("SELECT genre_id FROM sae.genre", engine)["genre_id"])

        with engine.begin() as conn:
            cleaning.preparer_liaison_ternaire(df_raw_tracks, ids_tracks, ids_albums, ids_artists).to_sql(
                "artist_album_track", conn, schema="sae", if_exists="append", index=False)
            
            cleaning.preparer_stats_echonest(df_raw_echonest, ids_tracks).to_sql(
                "stats_echonest", conn, schema="sae", if_exists="append", index=False, method=psql_insert_copy)

            # Insère le reste des liaisons ici (track_genre, etc.) comme avant
            cleaning.preparer_track_genre(df_raw_tracks, ids_genres).to_sql("track_genre", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_track_language(df_raw_tracks, engine).to_sql("track_language", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_album_tag(df_raw_albums, engine).to_sql("album_tag", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_track_tag(df_raw_tracks, engine).to_sql("track_tag", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_artist_tag(df_raw_artists, engine).to_sql("artist_tag", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_artist_language(df_raw_tracks, engine).to_sql("artist_language", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_track_genre_majoritaire(df_raw_tracks, engine).to_sql("track_genre_majoritaire", conn, schema="sae", if_exists="append", index=False)

            # Users Avancés
            cleaning.preparer_score_period(df_questionnaire, engine).to_sql("score_period", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_score_mood(df_questionnaire, engine).to_sql("score_mood", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_user_context(df_questionnaire, engine).to_sql("user_context", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_user_platform(df_questionnaire, engine).to_sql("user_platform", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_user_languages(df_questionnaire).to_sql("user_language", conn, schema="sae", if_exists="append", index=False)
            cleaning.preparer_genre_top_user(df_questionnaire, engine).to_sql("genre_top_user", conn, schema="sae", if_exists="append", index=False)

        # ÉTAPE 3 : DEEZER
        print("🌍 [ÉTAPE 3] Deezer...")
        harvest_everything(limit_count=2)
        
        with engine.begin() as conn:
            conn.execute(text("REFRESH MATERIALIZED VIEW sae.view_track_materialise;"))
        print("✅ Vue matérialisée mise à jour avec succès.")

        print("🔄 [ÉTAPE 4] Recalage des séquences SERIAL...")
        with engine.begin() as conn:
            recalage_sql = """
            DO $$ 
            DECLARE 
                row RECORD;
            BEGIN 
                FOR row IN (SELECT table_name, column_name 
                            FROM information_schema.columns 
                            WHERE table_schema = 'sae' 
                            AND column_default LIKE 'nextval%') 
                LOOP
                    EXECUTE format('SELECT setval(pg_get_serial_sequence(''sae.%I'', ''%I''), COALESCE(MAX(%I), 0) + 1, false) FROM sae.%I', 
                                   row.table_name, row.column_name, row.column_name, row.table_name);
                END LOOP;
            END $$;
            """
            conn.execute(text(recalage_sql))
            print("✅ Toutes les séquences ont été synchronisées avec les données importées.")

        print("✅ [SUCCESS] Terminé !")

if __name__ == "__main__":
    main()