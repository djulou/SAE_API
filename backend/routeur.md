# Documentation des Routes API 

## Données Musicales (Public)

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/album` | Récupère la liste de tous les albums. |
| `GET` | `/album/{album_id}` | Récupère les détails d'un album spécifique par son ID. |
| `GET` | `/track` | Récupère la liste de toutes les pistes. |
| `GET` | `/genres` | Récupère tous les genres musicaux (pour les menus/filtres). |
| `GET` | `/tags` | Récupère tous les tags disponibles. |
| `GET` | `/tracks/details` | Récupère les pistes avec détails (album, artiste) via une vue optimisée. |

## Utilisateur & Profil (Usage Interne / React)

Ces routes sont masquées de la documentation Swagger (`/docs`).

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/user/{email}` | Récupère un utilisateur par son email. |
| `GET` | `/users/{user_id}` | Récupère le profil complet d'un utilisateur (pseudo, email, image, etc.). |
| `GET` | `/users/{user_id}/stats` | Récupère les affinités musicales calculées (profil "radar"). |

## Statistiques d'Écoute (Privé)

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/users/{user_id}/listening-history` | Historique des 50 dernières playlists écoutées. |
| `GET` | `/users/{user_id}/top-tracks` | Top 10 des pistes les plus écoutées par l'utilisateur. |
| `GET` | `/users/{user_id}/top-albums` | Top 10 des albums les plus écoutés par l'utilisateur. |
| `GET` | `/users/{user_id}/listening-stats` | Totaux globaux (NB écoutes total, titres uniques, etc.). |

## Favoris & Playlists (Privé)

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `GET` | `/playlist` | Récupère toutes les playlists du système. |
| `GET` | `/playlists/user/{user_id}` | Récupère les playlists appartenant à un utilisateur précis. |
| `GET` | `/users/{user_id}/favorites/tracks` | Liste des chansons "aimées" par l'utilisateur. |
| `GET` | `/users/{user_id}/favorites/artists` | Liste des artistes suivis par l'utilisateur. |
| `GET` | `/users/{user_id}/favorites/albums` | Liste des albums mis en favoris. |

## Création de Données (POST)

| Méthode | Route | Corps de la requête (Schéma) |
| :--- | :--- | :--- |
| `POST` | `/user` | `UserCreate` (Création de compte) |
| `POST` | `/playlist` | `PlaylistCreate` (Créer une playlist) |
| `POST` | `/listeningHistory` | `ListeningHistoryCreate` (Ajouter un log d'écoute) |
| `POST` | `/UserAlbumListening` | `UserAlbumListeningCreate` (Incrémenter écoute album) |
| `POST` | `/UserPlaylistListening` | `UserPlaylistListeningCreate` (Incrémenter écoute playlist) |
| `POST` | `/PlaylistUserFavorite` | `PlaylistUserFavoriteCreate` (Aimer une playlist) |
| `POST` | `/TrackUserFavorite` | `TrackUserFavoriteCreate` (Aimer un titre) |
| `POST` | `/UserArtistFavorite` | `UserArtistFavoriteCreate` (Suivre un artiste) |
| `POST` | `/UserAlbumFavorite` | `UserAlbumFavoriteCreate` (Aimer un album) |
| `POST` | `/PlaylistTrack` | `PlaylistTrackCreate` (Ajouter un titre à une playlist) |

## Suppression de Données (DELETE)

### Anonymisation Utilisateur (RGPD)

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `DELETE` | `/user/{user_id}` | Anonymise toutes les données personnelles de l'utilisateur (email, pseudo, image, etc.). Les statistiques d'écoute sont conservées de manière anonyme. Conforme au droit à l'oubli du RGPD. |

### Gestion des Favoris

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `DELETE` | `/users/{user_id}/favorites/tracks/{track_id}` | Retire une piste des favoris de l'utilisateur. |
| `DELETE` | `/users/{user_id}/favorites/artists/{artist_id}` | Retire un artiste des favoris de l'utilisateur. |
| `DELETE` | `/users/{user_id}/favorites/albums/{album_id}` | Retire un album des favoris de l'utilisateur. |

### Gestion des Playlists

| Méthode | Route | Description |
| :--- | :--- | :--- |
| `DELETE` | `/playlists/{playlist_id}` | Supprime complètement une playlist (et tous ses liens avec les pistes). |
| `DELETE` | `/playlists/{playlist_id}/tracks/{track_id}` | Retire une piste spécifique d'une playlist. |

---
**Note sur la pagination** : Pour les routes de listes (genres, tags, album, etc.), vous pouvez utiliser les paramètres `skip` et `limit` dans l'URL (ex: `/album?skip=20&limit=20`).
