// =================================================================================
// |-                            Interfaces Principales
// =================================================================================

export interface Language {
    language_id: number;
    language_name?: string;
}

export interface AlbumType {
    type_id: number;
    type_name?: string;
}

export interface Artist {
    artist_id: number;
    artist_handle?: string;
    artist_name?: string;
    artist_bio?: string;
    artist_location?: string;
    artist_latitude?: number;
    artist_longitude?: number;
    artist_members?: string;
    artist_active_year_begin?: number;
    artist_year_end?: number;
    artist_favorites: number;
    artist_comments: number;
    artist_url?: string;
    artist_image_file?: string;
}

export interface Album {
    album_id: number;
    album_handle?: string;
    album_title?: string;
    album_information?: string;
    album_date_created: string; // Les DateTime sont reçus en string (ISO) par l'API
    album_date_released?: string;
    album_listens: number;
    album_favorites: number;
    album_comments: number;
    album_image_file?: string;
    album_url?: string;
    type_id?: number;
}

export interface Track {
    track_id: number;
    track_title?: string;
    track_duration?: number;
    track_listens: number;
    track_favorites: number;
    track_interest?: number;
    track_comments: number;
    track_date_created: string;
    track_composer?: string;
    license_id?: number;
}

export interface Genre {
    genre_id: number;
    genre_parent_id?: number;
    genre_title?: string;
    genre_handle?: string;
    genre_nb_tracks?: number;
}

// =================================================================================
// |-                            Utilisateurs
// =================================================================================

export interface User {
    user_id: number;
    email: string;
    pseudo?: string;
    login: string;
    image?: string;
    gender?: string;
    birth_year?: string;
    created_at: string;
    situation_name?: string;
}

export interface Playlist {
    playlist_id: number;
    playlist_name?: string;
    playlist_listens: number;
    user_id?: number;
}

// =================================================================================
// |-                            Vues (Données agrégées)
// =================================================================================

/**
 * Cette interface est particulièrement utile pour tes composants de listage
 * car elle regroupe déjà les infos de l'album et de l'artiste.
 */
export interface ViewTrackMaterialise {
    track_id: number;
    track_title?: string;
    track_duration?: number;
    track_interest?: number;
    track_date_created?: string;
    album_id?: number;
    album_title?: string;
    artist_id?: number;
    artist_name?: string;
    tags_list?: string;
    genres_list?: string;
    danceability?: number;
    energy?: number;
    tempo?: number;
    languages_list?: string;
}