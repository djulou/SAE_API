import re
import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize

from sqlalchemy import create_engine

# -------------------------
# Utilitaires de nettoyage
# -------------------------
def clean_text(s):
    if pd.isna(s):
        return ""
    # minuscules, enlève ponctuation sauf les underscores,
    # remplace les séparateurs de mots par espace
    s = str(s).lower()
    s = re.sub(r"[\W_]+", " ", s)  # remplace non-alphanum par espace
    s = re.sub(r"\s+", " ", s).strip()
    return s

def split_genres(genres_field):
    """
    Accepte :
      - une chaîne 'rock/pop' ou 'rock,pop' ou 'rock pop'
      - une liste Python ['rock','pop']
    Retourne une liste propre de genres (lowercase).
    """
    if pd.isna(genres_field):
        return []
    if isinstance(genres_field, list):
        tokens = genres_field
    else:
        # sépare sur | , ; / ou espaces multiples
        tokens = re.split(r"[|,/;]+|\s+", str(genres_field))
    tokens = [clean_text(t) for t in tokens if clean_text(t)]
    return tokens

# -------------------------
# Classe Recommender (Sans Audio/Echonest)
# -------------------------
class ContentRecommender:
    def __init__(self,
                 df,
                 text_columns = ("genre_title", "language_name", "track_title"),
                 artist_col="artist_name",
                 album_col="album_title",
                 tag_col="tags_list",
                 multi_genre_col="genres_list",    # colonne contenant plusieurs genres (ex: 'rock|pop')
                 maj_genre_col="track_genre_maj", # genre principal
                 tfidf_max_features=None):
        """
        df : DataFrame contenant au minimum track_id et colonnes listées ci-dessus.
        """
        self.df = df.copy().reset_index(drop=True)
        self.text_columns = text_columns
        self.artist_col = artist_col
        self.album_col = album_col
        self.tag_col = tag_col
        self.multi_genre_col = multi_genre_col
        self.maj_genre_col = maj_genre_col
        
        self.tfidf_max_features = tfidf_max_features

        # colonnes obligatoires check
        if "track_id" not in self.df.columns:
            raise ValueError("DataFrame must contain 'track_id' column")

        # build pipeline
        self._prepare_text_features()
        self._build_item_matrix()
        self._build_neighbors()

    # -------------------------
    # 1) Construire les "documents" textuels
    # -------------------------
    def _prepare_text_features(self):
        df = self.df

        # genres multiples -> list
        df["_genres_list"] = df.get(self.multi_genre_col, "").apply(split_genres)

        # tags multiples -> list
        df["_tags_list"] = df.get(self.tag_col, "").apply(split_genres)

        # track_genre_maj -> single token
        df["_maj_genre_tok"] = df.get(self.maj_genre_col, "").fillna("").apply(clean_text).replace("", np.nan).fillna("")

        # artist and album: prefix to avoid ambiguities and keep them as tokens
        df["_artist_tok"] = df.get(self.artist_col, "").fillna("").astype(str).apply(lambda s: "artist_" + clean_text(s).replace(" ", "_") if s.strip() else "")
        df["_album_tok"] = df.get(self.album_col, "").fillna("").astype(str).apply(lambda s: "album_" + clean_text(s).replace(" ", "_") if s.strip() else "")

        # basic text columns (genre_title, language, title)
        text_parts = []
        for col in self.text_columns:
            if col in df.columns:
                text_parts.append(df[col].fillna("").astype(str).apply(clean_text))
            else:
                text_parts.append(pd.Series([""] * len(df)))

        # join everything into a single string "document"
        docs = []
        for i, row in df.iterrows():
            parts = []
            # explicit genres list (join separated genres)
            parts += (row["_genres_list"] * 4) # On répète les genres 4 fois pour leur donner plus de poids
            # explicit tags list
            parts += (row["_tags_list"] * 2)
            # major genre token
            if row["_maj_genre_tok"]:
                parts.append(("majgenre_" + row["_maj_genre_tok"] + " ") * 5)
            # artist & album tokens (already prefixed)
            if row["_artist_tok"]:
                parts.append(row["_artist_tok"])
            # if row["_album_tok"]:
            #     parts.append(row["_album_tok"])
            # other text fields
            for col_series in text_parts:
                txt = col_series.iloc[i]
                if txt:
                    parts.append(txt)
            docs.append(" ".join(parts))

        df["text_features"] = docs
        self.df = df

    # -------------------------
    # 2) TF-IDF matrix
    # -------------------------
    def _build_tfidf(self):
        self.vectorizer = TfidfVectorizer(
            max_features=self.tfidf_max_features,
            stop_words="english",
            ngram_range=(1,2)  # unigrams + bigrams parfois utiles
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["text_features"].values)
        # vocabulary accessible via self.vectorizer.get_feature_names_out()

    # -------------------------
    # 3) Full item matrix (TF-IDF)
    # -------------------------
    def _build_item_matrix(self):
        self._build_tfidf()
        self.item_matrix = self.tfidf_matrix

    # -------------------------
    # 4) Similarity matrix
    # -------------------------
    def _build_neighbors(self, n_neighbors=50):
        self.nn = NearestNeighbors(
            n_neighbors=n_neighbors,
            metric="cosine",
            algorithm="brute"  # adapté au TF-IDF sparse
        )
        self.nn.fit(self.item_matrix)

    # -------------------------
    # 5) Recommandation : top-k similaires pour un track_id
    # -------------------------
    def recommend(self, track_id, top_k=10, same_artist_penalty=0.5):
        """
        same_artist_penalty : 
           0.0 -> Interdit totalement le même artiste
           0.5 -> Réduit le score de 50% (Il faut que la chanson soit très pertinente pour passer)
           1.0 -> Aucune pénalité (Résultat avec environ 80% d'artiste)
        """
        df = self.df
        if track_id not in df["track_id"].values:
            raise ValueError("track_id not present")

        idx = int(df.index[df["track_id"] == track_id][0])
        source_artist = df.iloc[idx][self.artist_col]

        # On prend plus de voisins pour avoir de la marge après pénalité
        distances, indices = self.nn.kneighbors(
            self.item_matrix[idx].reshape(1, -1),
            n_neighbors=top_k * 3 
        )

        similarities = 1 - distances.flatten()
        indices = indices.flatten()

        results = []
        for i, score in zip(indices, similarities):
            if i == idx: continue 
            
            row = df.iloc[i]
            current_score = score
            
            # Application de la pénalité si même artiste
            if row[self.artist_col] == source_artist:
                current_score *= same_artist_penalty
            
            # On ajoute tout
            results.append({
                "track_id": row["track_id"],
                "track_title": row["track_title"],
                "artist_name": row[self.artist_col],
                "score": current_score
            })

        # On trie à nouveau car les scores ont changé à cause de la pénalité
        results = sorted(results, key=lambda x: x['score'], reverse=True)
        
        # On ne garde que le top K
        return pd.DataFrame(results[:top_k])

    # -------------------------
    # Option : retourner scores complets (vecteur)
    # -------------------------
    def get_item_scores(self, track_id, top_k=50):
        df = self.df
        if track_id not in df["track_id"].values:
            raise ValueError("track_id not present")

        idx = int(df.index[df["track_id"] == track_id][0])

        distances, indices = self.nn.kneighbors(
            self.item_matrix[idx].reshape(1, -1),
            n_neighbors=top_k + 1
        )

        similarities = 1 - distances.flatten()
        indices = indices.flatten()

        mask = indices != idx
        return pd.DataFrame({
            "track_id": df.iloc[indices[mask]]["track_id"].values,
            "score": similarities[mask]
        })


# -------------------------
# Évaluation du système
# -------------------------

def evaluate_coherence(recommender, sample_size=100, top_k=5, same_artist_penalty=0.5):
    """
    Évalue la qualité technique des recommandations sur un échantillon aléatoire.
    Retourne un dictionnaire de métriques.
    """
    df = recommender.df
    
    # Vérification qu'on a assez de données
    real_sample_size = min(sample_size, len(df))
    sample_tracks = df.sample(n=real_sample_size, random_state=42)["track_id"].values
    
    metrics = {
        "same_artist_ratio": [],
        "same_maj_genre_ratio": [],
        "same_album_ratio": [],
        "avg_score": []
    }
    
    print(f"Évaluation en cours sur {real_sample_size} pistes (Top-{top_k}) same_artist_penalty = {same_artist_penalty}...")
    
    for query_id in sample_tracks:


        # 1. Récupérer les métadonnées de la piste source
        query_row = df[df["track_id"] == query_id].iloc[0]
        query_artist = query_row[recommender.artist_col]
        query_genre = query_row[recommender.maj_genre_col]
        query_album = query_row[recommender.album_col]
        
        if pd.isna(query_genre) or query_genre == "":
            skip_genre_eval = True
        else:
            skip_genre_eval = False

        # 2. Obtenir les recommandations
        try:
            # On demande top_k
            recs = recommender.recommend(query_id, top_k=top_k, same_artist_penalty=same_artist_penalty)
        except ValueError:
            continue
            
        if recs.empty:
            continue

        # 3. Récupérer les métadonnées des pistes recommandées
        # On fait une jointure pour récupérer artiste/genre/album des résultats
        recs_meta = df[df["track_id"].isin(recs["track_id"])].set_index("track_id")
        # On s'assure que l'ordre est respecté
        recs_meta = recs_meta.reindex(recs["track_id"])
        
        # 4. Calculs des correspondances (Booléens convertis en int 0 ou 1)
        # On gère les NaN en les considérant comme non-match
        
        # Artiste
        artist_match = (recs_meta[recommender.artist_col] == query_artist).mean()
        metrics["same_artist_ratio"].append(artist_match)
        
        # Genre Majeur
        if not skip_genre_eval:
            # On ne compare qu'avec les pistes recommandées qui ont AUSSI un genre
            valid_recs = recs_meta[recs_meta[recommender.maj_genre_col].notna()]
            if len(valid_recs) > 0:
                genre_match = (valid_recs[recommender.maj_genre_col] == query_genre).mean()
                metrics["same_maj_genre_ratio"].append(genre_match)
        
        # Album
        album_match = (recs_meta[recommender.album_col] == query_album).mean()
        metrics["same_album_ratio"].append(album_match)
        
        # Score moyen de similarité
        metrics["avg_score"].append(recs["score"].mean())

    # 5. Agrégation des résultats
    results = {
        "Global_Artist_Consistency": np.mean(metrics["same_artist_ratio"]),
        "Global_Genre_Consistency": np.mean(metrics["same_maj_genre_ratio"]),
        "Global_Album_Consistency": np.mean(metrics["same_album_ratio"]),
        "Average_Similarity_Score": np.mean(metrics["avg_score"])
    }
    
    return results

# engine = create_engine(
#     "postgresql+psycopg://postgres:uJ7A\\pgsql@127.0.0.1:5432/postgres"
# )

# # Modification de la requête : suppression des colonnes et des jointures echonest
# query = """
#         SELECT
#             t.track_id,
#             t.track_title,

#             -- artiste
#             ar.artist_name,

#             -- album
#             al.album_title AS album_name,

#             -- langues (peut y en avoir plusieurs)
#             STRING_AGG(DISTINCT lang.language_name, ' ') AS language_name,

#             -- genres multiples
#             STRING_AGG(DISTINCT g.genre_title, '|') AS genres,

#             -- tags multiples
#             STRING_AGG(DISTINCT tag.tag_name, '|') AS tags,

#             -- genre majoritaire
#             gmaj.genre_title AS track_genre_maj

#         FROM sae.Track t

#         -- lien artiste / album
#         LEFT JOIN sae.Artist_Album_Track aat ON aat.track_id = t.track_id
#         LEFT JOIN sae.Artist ar ON ar.artist_id = aat.artist_id
#         LEFT JOIN sae.Album al ON al.album_id = aat.album_id

#         -- genres multiples
#         LEFT JOIN sae.Track_Genre tg ON tg.track_id = t.track_id
#         LEFT JOIN sae.Genre g ON g.genre_id = tg.genre_id

#         -- tags multiples
#         LEFT JOIN sae.Track_Tag ttag ON ttag.track_id = t.track_id
#         LEFT JOIN sae.Tag tag ON tag.tag_id = ttag.tag_id

#         -- genre majoritaire
#         LEFT JOIN sae.Track_Genre_Majoritaire tgm ON tgm.track_id = t.track_id
#         LEFT JOIN sae.Genre gmaj ON gmaj.genre_id = tgm.genre_id

#         -- langues
#         LEFT JOIN sae.Track_Language tl ON tl.track_id = t.track_id
#         LEFT JOIN sae.Language lang ON lang.language_id = tl.language_id

#         GROUP BY
#             t.track_id,
#             t.track_title,
#             ar.artist_name,
#             al.album_title,
#             gmaj.genre_title;
#         """

# tracks_df = pd.read_sql(query, engine)


# query_listening = """
#     SELECT user_id, track_id, nb_listening 
#     FROM sae.user_track_listening;
# """

# listening_df = pd.read_sql(query_listening, engine)


# if __name__ == "__main__":
    
#     # 1. Initialisation du système de recommandation
#     print("Initialisation du moteur de recommandation...")
#     rec = ContentRecommender(tracks_df)
#     print("Moteur prêt.\n")

#     # 2. Choix de l'utilisateur Cible
#     TARGET_USER_ID = 1

#     print(f"--- Recherche pour l'utilisateur ID: {TARGET_USER_ID} ---")

#     # 3. Trouver le morceau le plus écouté pour cet utilisateur
#     # On filtre sur l'utilisateur
#     user_history = listening_df[listening_df["user_id"] == TARGET_USER_ID]

#     if user_history.empty:
#         print(f"Aucune donnée d'écoute trouvée pour l'utilisateur {TARGET_USER_ID}.")
#     else:
#         # On trie par nombre d'écoutes décroissant et on prend le premier
#         top_track_row = user_history.sort_values(by="nb_listening", ascending=False).iloc[0]
        
#         input_track_id = int(top_track_row["track_id"])
#         listen_count = top_track_row["nb_listening"]

#         # Récupération des infos du morceau (Titre/Artiste) pour affichage
#         # On regarde dans tracks_df car c'est là qu'on a les titres
#         track_info = tracks_df[tracks_df["track_id"] == input_track_id]
        
#         if track_info.empty:
#             print(f"Le morceau ID {input_track_id} a été écouté mais n'existe pas dans la base des morceaux (problème de cohérence).")
#         else:
#             track_title = track_info.iloc[0]["track_title"]
#             artist_name = track_info.iloc[0]["artist_name"]

#             print(f"Morceau le plus écouté : '{track_title}' par {artist_name} (ID: {input_track_id})")
#             print(f"Nombre d'écoutes : {listen_count}")
            
#             # 4. Lancer la recommandation basée sur ce morceau
#             print("\n--- Recommandations basées sur ce favori ---")
#             try:
#                 recs = rec.recommend(input_track_id, top_k=5, same_artist_penalty=0.5)
#                 print(recs.to_string(index=False))

#                 # print("\nSimilarity scores for track 2:")
#                 # print(rec.get_item_scores(2))


#                 # stats = evaluate_coherence(rec, sample_size=200, top_k=5, same_artist_penalty=0.7) # Baisser same_artist_penalty baisse artificiellement le score des morceaux
#                 #                                                                                    # du même artiste pour laisser la place à de nouveaux groupes (découverte)
#                 # print("\n--- RÉSULTATS DE L'ÉVALUATION ---")
#                 # print(f"Cohérence Genre   : {stats['Global_Genre_Consistency']:.2%} (Devrait être élevé > 80%)")
#                 # print(f"Cohérence Artiste : {stats['Global_Artist_Consistency']:.2%} (Dépend de la taille du catalogue)")
#                 # print(f"Cohérence Album   : {stats['Global_Album_Consistency']:.2%} (Indique si on recommande juste le même album)")
#                 # print(f"Score Moyen Sim.  : {stats['Average_Similarity_Score']:.4f} (Confiance moyenne)")
#                 # print("-----------------------------------")

#             except ValueError as e:
#                 print(f"Erreur lors de la recommandation : {e}")

