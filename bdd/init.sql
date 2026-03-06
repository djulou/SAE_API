DROP SCHEMA IF EXISTS sae CASCADE;
CREATE SCHEMA IF NOT EXISTS sae;
/*
* =================================================================================
* |-                            Tables principales
* =================================================================================
*/

create table sae.Language (
    language_id serial primary key,
    language_name varchar(50)
);

create table sae.Album_type (
    type_id serial primary key,
    type_name varchar(50)
);

create table sae.License (
    license_id serial primary key,
    license_name varchar(150)
);

create table sae.Tag (
    tag_id serial primary key,
    tag_name varchar(100)
);

create table sae.Genre (
    genre_id serial primary key,
    genre_parent_id int,
    genre_title varchar(50),
    genre_handle varchar(50),
    genre_nb_tracks int,
    FOREIGN KEY (genre_parent_id) REFERENCES sae.Genre (genre_id) ON DELETE CASCADE
);
CREATE INDEX idx_genre_parent ON sae.Genre(genre_parent_id);

create table sae.Platform (
    platform_id serial primary key,
    platform_name varchar(50)
);

create table sae.Period (
    period_id serial primary key,
    period_interval varchar(50)
);

create table sae.Context (
    context_id serial primary key,
    context_name varchar(50)
);

create table sae.Mood (
    mood_id serial primary key,
    mood_name varchar(50)
);

create table sae.Artist (
    artist_id BIGINT primary key,
    artist_handle varchar(150),
    artist_name varchar(150),
    artist_bio varchar(40000),
    artist_location varchar(500),
    artist_latitude float,
    artist_longitude float,
    artist_members varchar(7000),
    artist_associated_labels varchar(255),
    artist_related_projects varchar(1500),
    artist_active_year_begin int,
    artist_year_end int,
    artist_contact varchar(255),
    artist_favorites int DEFAULT(0),
    artist_comments int DEFAULT(0),
    artist_url varchar(255),
    artist_image_file varchar(255)
);
CREATE INDEX idx_artist_name ON sae.Artist(artist_name);

create table sae.Album (
    album_id BIGINT primary key,
    album_handle varchar(150),
    album_title varchar(150),
    album_information varchar(50000),
    album_date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    album_date_released date,
    album_listens int DEFAULT(0),
    album_favorites int DEFAULT(0),
    album_comments int DEFAULT(0),
    album_producer varchar(255),
    album_engineer varchar(255),
    album_image_file varchar(255),
    album_url varchar(255),
    type_id int,
    FOREIGN KEY (type_id) REFERENCES sae.Album_type (type_id) ON DELETE SET NULL
);
CREATE INDEX idx_album_type ON sae.Album(type_id);
CREATE INDEX idx_album_title ON sae.Album(album_title);

create table sae.Track (
    track_id BIGINT primary key,
    track_title varchar(255),
    track_duration float,
    track_listens int DEFAULT(0),
    track_favorites int DEFAULT(0),
    track_interest float,
    track_comments int DEFAULT(0),
    track_date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    track_date_recorded date,
    track_composer varchar(255),
    track_lyricist varchar(255),
    track_publisher varchar(255),
    license_id int,
    preview VARCHAR(512),
    FOREIGN KEY (license_id) REFERENCES sae.License (license_id) ON DELETE SET NULL
);
CREATE INDEX idx_track_license ON sae.Track(license_id);
CREATE INDEX idx_track_title ON sae.Track(track_title);

create table sae.Stats_echonest (
    track_id BIGINT primary key,
    acousticness float,
    danceability float,
    energy float,
    instrumentalness float,
    liveness float,
    speechness float,
    tempo float,
    valence float,
    currency int,
    hotness int,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE
);

/*
* =================================================================================
* |-                            Utilisateurs et derives
* =================================================================================
*/

create table sae.User (
    user_id serial primary key,
    liked_tracks int DEFAULT(0),
    email varchar(100) NOT NULL UNIQUE,
    image varchar(255),
    pseudo varchar(50),
    user_login varchar(50) NOT NULL UNIQUE,
    user_mdp varchar(64) NOT NULL,
    user_gender char,
    birth_year date,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    situation_name varchar(50),
    frequency_interval varchar(50),
    last_calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create table sae.Search_History (
    history_id serial primary key,
    history_query varchar(255),
    history_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE
);
CREATE INDEX idx_history_user ON sae.Search_History(user_id);

create table sae.Stats_user (
    stat_user_id serial primary key,
    danceability_affinity float,
    energy_affinity float,
    instrumentalness_affinity float,
    liveness_affinity float,
    speechness_affinity float,
    tempo_affinity float,
    valence_affinity float,
    currency_affinity float,
    hotness_affinity float,
    user_id int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    UNIQUE (user_id)
);

create table sae.Playlist (
    playlist_id serial primary key,
    playlist_name varchar(100),
    playlist_listens int default 0,
    user_id int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE
);
CREATE INDEX idx_playlist_user ON sae.Playlist(user_id);

/*
* =================================================================================
* |-                        Relations (Tables de liaison)
* =================================================================================
*/

create table sae.Artist_Album_Track (
    artist_id BIGINT,
    album_id BIGINT,
    track_id BIGINT,
    FOREIGN KEY (artist_id) REFERENCES sae.Artist (artist_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES sae.Album (album_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    primary key (artist_id, album_id, track_id)
);
CREATE INDEX idx_aat_album ON sae.Artist_Album_Track(album_id);
CREATE INDEX idx_aat_track ON sae.Artist_Album_Track(track_id);

create table sae.Playlist_User_Favorite (
    user_id INT,
    playlist_id INT,
    added_at date DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES sae.Playlist (playlist_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, playlist_id)
);
CREATE INDEX idx_puf_playlist ON sae.Playlist_User_Favorite(playlist_id);

create table sae.Playlist_User (
    user_id INT,
    playlist_id INT,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES sae.Playlist (playlist_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, playlist_id)
);
CREATE INDEX idx_pu_playlist ON sae.Playlist_User(playlist_id);

create table sae.Playlist_Track (
    playlist_id int,
    track_id BIGINT,
    PRIMARY KEY (playlist_id, track_id),
    FOREIGN KEY (playlist_id) REFERENCES sae.Playlist (playlist_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE
);
CREATE INDEX idx_pt_track ON sae.Playlist_Track(track_id);

create table sae.User_Context (
    user_id int,
    context_id int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (context_id) REFERENCES sae.Context (context_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, context_id)
);
CREATE INDEX idx_uc_context ON sae.User_Context(context_id);

create table sae.Score_Mood (
    user_id int,
    mood_id int,
    affinity_score float DEFAULT(0),
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (mood_id) REFERENCES sae.Mood (mood_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, mood_id)
);
CREATE INDEX idx_sm_mood ON sae.Score_Mood(mood_id);

create table sae.User_Platform (
    user_id int,
    platform_id int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (platform_id) REFERENCES sae.Platform (platform_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, platform_id)
);
CREATE INDEX idx_up_platform ON sae.User_Platform(platform_id);

create table sae.Score_Period (
    user_id int,
    period_id int,
    affinity_score float DEFAULT(0),
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (period_id) REFERENCES sae.Period (period_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, period_id)
);
CREATE INDEX idx_sp_period ON sae.Score_Period(period_id);

create table sae.User_Track_Listening (
    user_id int,
    track_id BIGINT,
    nb_listening int DEFAULT(1),
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, track_id)
);
CREATE INDEX idx_utl_track ON sae.User_Track_Listening(track_id);

create table sae.Track_User_Favorite (
    user_id int,
    track_id BIGINT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, track_id)
);
CREATE INDEX idx_tuf_track ON sae.Track_User_Favorite(track_id);

create table sae.Track_Genre (
    track_id BIGINT,
    genre_id int,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES sae.Genre (genre_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, genre_id)
);
CREATE INDEX idx_tg_genre ON sae.Track_Genre(genre_id);

create table sae.Track_Genre_Majoritaire (
    track_id BIGINT,
    genre_id int,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES sae.Genre (genre_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, genre_id)
);
CREATE INDEX idx_tgm_genre ON sae.Track_Genre_Majoritaire(genre_id);

create table sae.Genre_top_User (
    user_id int,
    genre_id int,
    genre_rate float,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES sae.Genre (genre_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, genre_id)
);
CREATE INDEX idx_gtu_genre ON sae.Genre_top_User(genre_id);

create table sae.Track_Language (
    track_id BIGINT,
    language_id int,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES sae.Language (language_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, language_id)
);
CREATE INDEX idx_tl_language ON sae.Track_Language(language_id);

create table sae.Album_Tag (
    album_id BIGINT,
    tag_id int,
    FOREIGN KEY (album_id) REFERENCES sae.Album (album_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES sae.Tag (tag_id) ON DELETE CASCADE,
    PRIMARY KEY (album_id, tag_id)
);
CREATE INDEX idx_at_tag ON sae.Album_Tag(tag_id);

create table sae.Track_Tag(
    track_id BIGINT,
    tag_id int,
    FOREIGN KEY (track_id) REFERENCES sae.Track (track_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES sae.Tag (tag_id) ON DELETE CASCADE,
    PRIMARY KEY (track_id, tag_id)
);
CREATE INDEX idx_tt_tag ON sae.Track_Tag(tag_id);

create table sae.Artist_Tag(
    artist_id BIGINT,
    tag_id int,
    FOREIGN KEY (artist_id) REFERENCES sae.Artist (artist_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES sae.Tag (tag_id) ON DELETE CASCADE,
    PRIMARY KEY (artist_id, tag_id)
);
CREATE INDEX idx_art_tag ON sae.Artist_Tag(tag_id);

create table sae.User_Artist_Favorite(
    artist_id BIGINT,
    user_id int,
    FOREIGN KEY (artist_id) REFERENCES sae.Artist (artist_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    PRIMARY KEY (artist_id, user_id)
);

CREATE INDEX idx_uaf_user ON sae.User_Artist_Favorite(user_id);

create table sae.Artist_Language (
    artist_id BIGINT,
    language_id int,
    FOREIGN KEY (artist_id) REFERENCES sae.Artist (artist_id) ON DELETE CASCADE,
    FOREIGN KEY (language_id) REFERENCES sae.Language (language_id) ON DELETE CASCADE,
    PRIMARY KEY (artist_id, language_id)
);
CREATE INDEX idx_al_language ON sae.Artist_Language(language_id);

CREATE TABLE sae.Listening_History (
    history_id   SERIAL PRIMARY KEY,
    user_id      INT,
    playlist_id  INT,
    listened_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sae.User(user_id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES sae.Playlist(playlist_id) ON DELETE CASCADE
);
CREATE INDEX idx_lh_user ON sae.Listening_History(user_id);
CREATE INDEX idx_lh_playlist ON sae.Listening_History(playlist_id);

create table sae.User_Album_Favorite (
    user_id int,
    album_id BIGINT,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES sae.Album (album_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, album_id)
);
CREATE INDEX idx_uaf_album ON sae.User_Album_Favorite(album_id);

create table sae.User_Album_Listening (
    user_id int,
    album_id BIGINT,
    nb_listening int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES sae.Album (album_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, album_id)
);
CREATE INDEX idx_ual_album ON sae.User_Album_Listening(album_id);

create table sae.User_Playlist_Listening (
    user_id int,
    playlist_id int,
    nb_listening int,
    FOREIGN KEY (user_id) REFERENCES sae.User (user_id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES sae.Playlist (playlist_id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, playlist_id)
);
CREATE INDEX idx_upl_playlist ON sae.User_Playlist_Listening(playlist_id);

/*
* =================================================================================
* |-                             Roles / Permissions
* =================================================================================
*/

-- Liste des rôles possibles (ADMIN, USER, ARTIST)
CREATE TABLE sae.Role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- Liste des actions possibles (create_playlist, delete_any_track, edit_artist, create_track)
CREATE TABLE sae.Permission (
    permission_id SERIAL PRIMARY KEY,
    permission_label VARCHAR(100) UNIQUE NOT NULL
);

-- Table de liaison : quel rôle possède quelle permission ?
CREATE TABLE sae.Role_Permission (
    role_id INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    
    CONSTRAINT fk_role_id 
        FOREIGN KEY (role_id) 
        REFERENCES sae.Role(role_id) 
        ON DELETE CASCADE,
        
    CONSTRAINT fk_permission_id 
        FOREIGN KEY (permission_id) 
        REFERENCES sae.Permission(permission_id) 
        ON DELETE CASCADE
);

-- Table de liaison : quel utilisateur a quel rôle ?
CREATE TABLE sae.User_Role (
    user_id INT,
    role_id INT,
    PRIMARY KEY (user_id, role_id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES sae.User(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_role FOREIGN KEY (role_id) REFERENCES sae.Role(role_id) ON DELETE CASCADE
);

INSERT INTO sae.Role (role_name) VALUES 
('ADMIN'), 
('MODERATOR'), 
('ARTIST'), 
('USER');

INSERT INTO sae.Permission (permission_label) VALUES 
-- Permissions de base (USER)
('track_listen'),          -- Droit d'écouter et d'incrémenter les stats
('track_like'),            -- Ajouter aux favoris
('playlist_create'),       -- Créer ses propres listes
('playlist_edit_own'),     -- Modifier ses propres listes

-- Permissions avancées (ARTIST / MODERATOR)
('track_upload'),          -- Publier un nouveau morceau
('album_create'),          -- Créer un album
('track_edit_own'),        -- Modifier ses propres morceaux

-- Permissions de contrôle (ADMIN)
('user_ban'),              -- Désactiver un compte
('track_delete_any'),      -- Modération de contenu
('role_manage');           -- Modifier les droits des autres

-- Droits pour le rôle USER (ID 4 si on suit l'ordre d'insertion)
INSERT INTO sae.Role_Permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM sae.Role r, sae.Permission p
WHERE r.role_name = 'USER' 
AND p.permission_label IN ('track_listen', 'track_like', 'playlist_create', 'playlist_edit_own');

-- Droits pour le rôle ARTIST (USER + Uploads)
INSERT INTO sae.Role_Permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM sae.Role r, sae.Permission p
WHERE r.role_name = 'ARTIST' 
AND p.permission_label IN ('track_listen', 'track_like', 'playlist_create', 'playlist_edit_own', 'track_upload', 'album_create', 'track_edit_own');

-- Droits pour l'ADMIN (Tout)
INSERT INTO sae.Role_Permission (role_id, permission_id)
SELECT r.role_id, p.permission_id
FROM sae.Role r, sae.Permission p
WHERE r.role_name = 'ADMIN';


/*
* =================================================================================
* |-                             Fonctions / Triggers
* =================================================================================
*/
-- 1. On corrige la fonction pour gérer le schéma proprement
CREATE OR REPLACE FUNCTION update_generic_listens()
RETURNS TRIGGER AS $$
DECLARE
    fk_column_name TEXT;
    target_table   TEXT;
    target_column  TEXT;
    record_id      BIGINT;
    diff           INT;
BEGIN
    fk_column_name := TG_ARGV[0]; 
    target_table   := TG_ARGV[1]; -- On attend juste 'track', 'album', etc.
    target_column  := TG_ARGV[2];

    -- Calcul de la différence (+N ou -N)
    IF (TG_OP = 'INSERT') THEN
        diff := NEW.nb_listening;
    ELSIF (TG_OP = 'UPDATE') THEN
        diff := NEW.nb_listening - OLD.nb_listening;
    ELSE
        RETURN NULL;
    END IF;

    -- Si pas de changement, on ne fait rien
    IF diff = 0 THEN
        RETURN NEW;
    END IF;

    -- Récupération de l'ID via la colonne dynamique (ex: NEW.track_id)
    EXECUTE format('SELECT ($1).%I', fk_column_name) 
    USING NEW 
    INTO record_id;

    -- MISE A JOUR : On force le schéma 'sae' ici, et %I ne gère que le nom de la table
    EXECUTE format('UPDATE sae.%I SET %I = %I + $1 WHERE %I = $2', 
                   target_table, target_column, target_column, fk_column_name)
    USING diff, record_id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 2. On recrée les triggers avec les noms de tables EN MINUSCULE et SANS 'sae.'

DROP TRIGGER IF EXISTS trg_update_track_listens ON sae.User_Track_Listening;
CREATE TRIGGER trg_update_track_listens
AFTER INSERT OR UPDATE ON sae.User_Track_Listening
FOR EACH ROW
EXECUTE FUNCTION update_generic_listens('track_id', 'track', 'track_listens');

DROP TRIGGER IF EXISTS trg_update_playlist_listens ON sae.User_Playlist_Listening;
CREATE TRIGGER trg_update_playlist_listens
AFTER INSERT OR UPDATE ON sae.User_Playlist_Listening
FOR EACH ROW
EXECUTE FUNCTION update_generic_listens('playlist_id', 'playlist', 'playlist_listens');

DROP TRIGGER IF EXISTS trg_update_album_listens ON sae.User_Album_Listening;
CREATE TRIGGER trg_update_album_listens
AFTER INSERT OR UPDATE ON sae.User_Album_Listening
FOR EACH ROW
EXECUTE FUNCTION update_generic_listens('album_id', 'album', 'album_listens');

CREATE OR REPLACE FUNCTION update_genre_nb_tracks()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE sae.Genre
        SET genre_nb_tracks = genre_nb_tracks + 1
        WHERE genre_id = NEW.genre_id;
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE sae.Genre
        SET genre_nb_tracks = genre_nb_tracks - 1
        WHERE genre_id = OLD.genre_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ language 'plpgsql';

CREATE TRIGGER trg_track_genre_count
AFTER INSERT OR DELETE ON sae.Track_Genre
FOR EACH ROW
EXECUTE PROCEDURE update_genre_nb_tracks();

CREATE OR REPLACE FUNCTION update_parent_genre_tracks()
RETURNS TRIGGER AS $$
DECLARE
  diff INT;
  curr_parent_id INT;
BEGIN
  diff := NEW.genre_nb_tracks - OLD.genre_nb_tracks;
  
  IF diff = 0 THEN RETURN NEW; END IF;

  curr_parent_id := NEW.genre_parent_id;

  WHILE curr_parent_id IS NOT NULL LOOP
    UPDATE sae.Genre
    SET genre_nb_tracks = genre_nb_tracks + diff
    WHERE genre_id = curr_parent_id
    RETURNING genre_parent_id INTO curr_parent_id;
  END LOOP;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_genre_nb_tracks_parent
AFTER UPDATE ON sae.Genre
FOR EACH ROW
WHEN (OLD.genre_nb_tracks IS DISTINCT FROM NEW.genre_nb_tracks)
EXECUTE FUNCTION update_parent_genre_tracks();

CREATE OR REPLACE FUNCTION majGenresTop(p_user_id INT)
RETURNS void AS $$
BEGIN
    WITH RawScores AS (
        SELECT 
            utl.user_id,
            tg.genre_id,
            (utl.nb_listening * 1) as points 
        FROM sae.User_Track_Listening utl
        JOIN sae.Track_Genre tg ON utl.track_id = tg.track_id
        WHERE utl.user_id = p_user_id
        
        UNION ALL
        
        SELECT 
            utl.user_id,
            tgm.genre_id,
            (utl.nb_listening * 2) as points
        FROM sae.User_Track_Listening utl
        JOIN sae.Track_Genre_Majoritaire tgm ON utl.track_id = tgm.track_id
        WHERE utl.user_id = p_user_id
    ),
    GenreStats AS (
        SELECT 
            user_id,
            genre_id,
            SUM(points) as score_genre,
            SUM(SUM(points)) OVER (PARTITION BY user_id) as total_points_user
        FROM RawScores
        GROUP BY user_id, genre_id
    )
    INSERT INTO sae.Genre_top_User (user_id, genre_id, genre_rate)
    SELECT 
        user_id,
        genre_id,
        ROUND((score_genre::numeric / NULLIF(total_points_user, 0)::numeric), 4)
    FROM GenreStats
    WHERE total_points_user > 0
    ON CONFLICT (user_id, genre_id) 
    DO UPDATE SET 
        genre_rate = EXCLUDED.genre_rate;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION sae.majStats(p_user_id INT)
RETURNS void AS $$
BEGIN
    SET LOCAL app.internal_update = 'true';

    WITH UserAudioProfile AS (
        SELECT 
            utl.user_id,
            SUM(utl.nb_listening) as total_ecoutes,
            SUM(s.danceability * utl.nb_listening)     / NULLIF(SUM(utl.nb_listening), 0) as avg_dance,
            SUM(s.energy * utl.nb_listening)           / NULLIF(SUM(utl.nb_listening), 0) as avg_energy,
            SUM(s.instrumentalness * utl.nb_listening) / NULLIF(SUM(utl.nb_listening), 0) as avg_instru,
            SUM(s.liveness * utl.nb_listening)         / NULLIF(SUM(utl.nb_listening), 0) as avg_live,
            SUM(s.speechness * utl.nb_listening)       / NULLIF(SUM(utl.nb_listening), 0) as avg_speech,
            SUM(s.tempo * utl.nb_listening)            / NULLIF(SUM(utl.nb_listening), 0) as avg_tempo,
            SUM(s.valence * utl.nb_listening)          / NULLIF(SUM(utl.nb_listening), 0) as avg_valence
        FROM sae.User_Track_Listening utl
        JOIN sae.Stats_echonest s ON utl.track_id = s.track_id
        WHERE utl.user_id = p_user_id
        GROUP BY utl.user_id
    )
    INSERT INTO sae.Stats_user (
        user_id, danceability_affinity, energy_affinity, instrumentalness_affinity, 
        liveness_affinity, speechness_affinity, tempo_affinity, valence_affinity
    )
    SELECT 
        user_id, avg_dance, avg_energy, avg_instru, avg_live, avg_speech, 
        avg_tempo, avg_valence
    FROM UserAudioProfile
    WHERE total_ecoutes > 0
    ON CONFLICT (user_id) DO UPDATE SET 
        danceability_affinity     = EXCLUDED.danceability_affinity,
        energy_affinity           = EXCLUDED.energy_affinity,
        instrumentalness_affinity = EXCLUDED.instrumentalness_affinity,
        liveness_affinity         = EXCLUDED.liveness_affinity,
        speechness_affinity       = EXCLUDED.speechness_affinity,
        tempo_affinity            = EXCLUDED.tempo_affinity,
        valence_affinity          = EXCLUDED.valence_affinity,
        currency_affinity         = COALESCE(sae.Stats_user.currency_affinity, 0),
        hotness_affinity          = COALESCE(sae.Stats_user.hotness_affinity, 0);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION trg_majStats_func()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        PERFORM sae.majStats(OLD.user_id);
        RETURN OLD;
    ELSE
        PERFORM sae.majStats(NEW.user_id);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_listening_change
AFTER INSERT OR UPDATE OR DELETE ON sae.User_Track_Listening
FOR EACH ROW EXECUTE FUNCTION trg_majStats_func();

CREATE OR REPLACE FUNCTION majPeriod(p_user_id INT)
RETURNS void AS $$
BEGIN
    WITH StatsCalculees AS (
        SELECT 
            l.user_id,
            CASE 
                WHEN EXTRACT(YEAR FROM t.track_date_created) >= 2020 THEN 1
                WHEN EXTRACT(YEAR FROM t.track_date_created) >= 2010 THEN 2
                WHEN EXTRACT(YEAR FROM t.track_date_created) >= 2000 THEN 3
                WHEN EXTRACT(YEAR FROM t.track_date_created) >= 1990 THEN 4
                WHEN EXTRACT(YEAR FROM t.track_date_created) >= 1980 THEN 5
                ELSE 6 
            END as calculated_period_id,
            
            SUM(l.nb_listening) as ecoutes_periode,
            SUM(SUM(l.nb_listening)) OVER (PARTITION BY l.user_id) as ecoutes_totales
        FROM sae.User_Track_Listening l
        JOIN sae.Track t ON l.track_id = t.track_id
        WHERE l.user_id = p_user_id
        GROUP BY l.user_id, calculated_period_id
    )
    INSERT INTO sae.Score_Period (user_id, period_id, affinity_score)
    SELECT 
        user_id,
        calculated_period_id,
        ROUND((ecoutes_periode::numeric / NULLIF(ecoutes_totales, 0)::numeric), 4)
    FROM StatsCalculees
    WHERE ecoutes_totales > 0
    ON CONFLICT (user_id, period_id) 
    DO UPDATE SET affinity_score = EXCLUDED.affinity_score;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION count_favorites_track(function_track_id bigint)
RETURNS INT AS $$
DECLARE
    user_favorites_count INT;
    base_track_favorites INT;
BEGIN
    SELECT COUNT(*) INTO user_favorites_count FROM sae.Track_User_Favorite WHERE track_id = function_track_id;
    SELECT track_favorites INTO base_track_favorites FROM sae.Track WHERE track_id = function_track_id;

    RETURN user_favorites_count + COALESCE(base_track_favorites, 0);
END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION count_favorites_album(function_album_id bigint)
RETURNS INT AS $$
DECLARE
    user_favorites_count INT;
    base_album_favorites INT;
BEGIN
    SELECT COUNT(*) INTO user_favorites_count FROM sae.User_Album_Favorite WHERE album_id = function_album_id;
    SELECT album_favorites INTO base_album_favorites FROM sae.Album WHERE album_id = function_album_id;

    RETURN user_favorites_count + COALESCE(base_album_favorites, 0);
END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION count_favorites_playlist(function_playlist_id bigint)
RETURNS INT AS $$
DECLARE
    favorites_count INT;
BEGIN
    SELECT COUNT(*) INTO favorites_count FROM sae.Playlist_User_Favorite WHERE playlist_id = function_playlist_id;
    RETURN favorites_count;
END;
$$ LANGUAGE 'plpgsql';

CREATE OR REPLACE FUNCTION majHistory() RETURNS trigger AS $$
DECLARE
  history_limit CONSTANT integer := 20; 
  history_count integer;
BEGIN
  SELECT count(*) INTO history_count FROM sae.Search_History WHERE user_id = NEW.user_id;
  
  IF history_count >= history_limit THEN
    DELETE FROM sae.Search_History
    WHERE history_id = (
        SELECT history_id 
        FROM sae.Search_History 
        WHERE user_id = NEW.user_id 
        ORDER BY history_timestamp ASC 
        LIMIT 1
    );
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tg_majHistory
  BEFORE INSERT ON sae.Search_History
  FOR EACH ROW
  EXECUTE PROCEDURE majHistory();

CREATE OR REPLACE FUNCTION majGlobal() RETURNS trigger AS $$
DECLARE
  v_last_calculated_at TIMESTAMP;
BEGIN
  SELECT last_calculated_at INTO v_last_calculated_at FROM sae.User WHERE user_id = NEW.user_id;

  IF v_last_calculated_at IS NULL OR v_last_calculated_at < (NOW() - INTERVAL '7 days') THEN
    PERFORM majPeriod(NEW.user_id);
    PERFORM majStats(NEW.user_id);
    PERFORM majGenresTop(NEW.user_id);

    UPDATE sae.User SET last_calculated_at = NOW() WHERE user_id = NEW.user_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER tg_majGlobal
  AFTER INSERT ON sae.User_Track_Listening
  FOR EACH ROW
  EXECUTE PROCEDURE majGlobal();

CREATE OR REPLACE FUNCTION sae.initStatFunc() 
RETURNS TRIGGER AS $$
BEGIN 
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
    VALUES (
        NEW.user_id,
        0, 0, 0, 0, 0, 0, 0, 0, 0
    );

    RETURN NEW; 
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_init_stats
    AFTER INSERT ON sae.User
    FOR EACH ROW
    EXECUTE FUNCTION sae.initStatFunc();

CREATE OR REPLACE FUNCTION sae.block_manual_changes()
RETURNS TRIGGER AS $$
DECLARE
    is_internal TEXT;
BEGIN
    -- On récupère la valeur de notre variable (on utilise coalesce pour éviter les erreurs si elle n'existe pas)
    is_internal := current_setting('app.internal_update', true);

    -- Si la variable est à 'true', on laisse passer la modification
    IF is_internal = 'true' THEN
        RETURN NEW;
    END IF;

    -- Sinon, c'est une modification manuelle (ex: via l'API ou un client SQL), on bloque
    RAISE EXCEPTION 'Interdiction de modifier manuellement sae.Stats_user. Utilisez les triggers de la table User.';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_protect_stats ON sae.Stats_user;

CREATE TRIGGER trg_protect_stats
    BEFORE UPDATE ON sae.Stats_user
    FOR EACH ROW
    EXECUTE FUNCTION sae.block_manual_changes();

CREATE OR REPLACE FUNCTION sae.tg_assign_default_role()
RETURNS TRIGGER AS $$
DECLARE
    default_role_id INT;
BEGIN
    -- 1. On récupère l'ID du rôle par défaut (ex: 'USER')
    -- On utilise COALESCE pour éviter de planter si le rôle n'existe pas encore
    SELECT role_id INTO default_role_id FROM sae.Role WHERE role_name = 'USER';

    -- 2. Si le rôle existe, on l'attribue au nouvel utilisateur
    IF default_role_id IS NOT NULL THEN
        INSERT INTO sae.User_Role (user_id, role_id)
        VALUES (NEW.user_id, default_role_id);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_after_user_insert
AFTER INSERT ON sae.User
FOR EACH ROW
EXECUTE FUNCTION sae.tg_assign_default_role();

/*
* =================================================================================
* |-                    TRIGGERS POUR LA PLAYLIST "TITRES AIMÉS"
* =================================================================================
*/
-- Fonction pour créer la playlist "Titres aimés" lors de la création d'un utilisateur
CREATE OR REPLACE FUNCTION sae.create_liked_tracks_playlist()
RETURNS TRIGGER AS $$
DECLARE
    new_playlist_id INT;
BEGIN
    -- Créer la playlist "Titres aimés"
    INSERT INTO sae.Playlist (playlist_name, user_id)
    VALUES ('Titres aimés', NEW.user_id)
    RETURNING playlist_id INTO new_playlist_id;
    
    -- Lie la playlist à l'utilisateur dans Playlist_User
    INSERT INTO sae.Playlist_User (user_id, playlist_id)
    VALUES (NEW.user_id, new_playlist_id);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- Trigger qui s'exécute après la création d'un utilisateur
CREATE TRIGGER trigger_create_liked_tracks_playlist
AFTER INSERT ON sae.User
FOR EACH ROW
EXECUTE FUNCTION sae.create_liked_tracks_playlist();
-- Fonction pour ajouter automatiquement un titre aimé à la playlist "Titres aimés"
CREATE OR REPLACE FUNCTION sae.add_to_liked_tracks_playlist()
RETURNS TRIGGER AS $$
DECLARE
    liked_playlist_id INT;
BEGIN
    SELECT p.playlist_id INTO liked_playlist_id
    FROM sae.Playlist p
    WHERE p.user_id = NEW.user_id 
    AND p.playlist_name = 'Titres aimés'
    LIMIT 1;
    
    -- Si la playlist existe, ajouter le titre dedans (s'il n'y est pas déjà)
    IF liked_playlist_id IS NOT NULL THEN
        INSERT INTO sae.Playlist_Track (playlist_id, track_id)
        VALUES (liked_playlist_id, NEW.track_id)
        ON CONFLICT (playlist_id, track_id) DO NOTHING;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
-- Trigger qui s'exécute après l'ajout d'un favori
CREATE TRIGGER trigger_add_to_liked_tracks_playlist
AFTER INSERT ON sae.Track_User_Favorite
FOR EACH ROW
EXECUTE FUNCTION sae.add_to_liked_tracks_playlist();
-- Fonction pour retirer automatiquement un titre de la playlist quand on retire le like
CREATE OR REPLACE FUNCTION sae.remove_from_liked_tracks_playlist()
RETURNS TRIGGER AS $$
DECLARE
    liked_playlist_id INT;
BEGIN
    SELECT p.playlist_id INTO liked_playlist_id
    FROM sae.Playlist p
    WHERE p.user_id = OLD.user_id 
    AND p.playlist_name = 'Titres aimés'
    LIMIT 1;
    
    -- Si la playlist existe, retire le titre
    IF liked_playlist_id IS NOT NULL THEN
        DELETE FROM sae.Playlist_Track 
        WHERE playlist_id = liked_playlist_id 
        AND track_id = OLD.track_id;
    END IF;
    
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
-- Trigger qui s'exécute après la suppression d'un favori
CREATE TRIGGER trigger_remove_from_liked_tracks_playlist
AFTER DELETE ON sae.Track_User_Favorite
FOR EACH ROW
EXECUTE FUNCTION sae.remove_from_liked_tracks_playlist();

/*
* =================================================================================
* |-                                    Vues
* =================================================================================
*/

CREATE OR REPLACE VIEW sae.View_User AS
SELECT user_id, pseudo, image, situation_name, birth_year, liked_tracks, user_login, email, user_gender, last_calculated_at, user_mdp
FROM sae.User;

DROP MATERIALIZED VIEW IF EXISTS sae.View_Track_Materialise CASCADE;

CREATE MATERIALIZED VIEW sae.view_track_materialise AS
SELECT
    t.track_id,
    t.track_title,
    t.track_duration,
    t.track_interest, 
    t.track_comments,
    t.track_date_created,
    t.track_date_recorded,
    t.track_listens,
    t.track_composer,
    t.track_lyricist,
    t.track_publisher,
    t.license_id,
    t.preview,
    alb.album_id,
    alb.album_title,
    alb.album_handle,
    alb.album_information,
    alb.album_date_created,
    alb.album_date_released,
    alb.album_engineer,
    alb.album_producer,
    alb.album_image_file,
    a.artist_id,
    a.artist_location,
    gmaj.genre_title AS track_genre_maj,
    a.artist_name,
    STRING_AGG(DISTINCT tag.tag_name, ', ') AS tags_list,
    STRING_AGG(DISTINCT g.genre_title, ', ') AS genres_list,
    s.danceability,
    s.energy,
    s.tempo,
    STRING_AGG(DISTINCT l.language_name, ', ') AS languages_list
FROM
    sae.Track t
    JOIN sae.Artist_Album_Track aat ON t.track_id = aat.track_id
    JOIN sae.Artist a ON aat.artist_id = a.artist_id
    JOIN sae.Album alb ON aat.album_id = alb.album_id
    LEFT JOIN sae.Stats_echonest s ON t.track_id = s.track_id
    LEFT JOIN sae.Track_Tag tt ON tt.track_id = t.track_id
    LEFT JOIN sae.Tag tag ON tt.tag_id = tag.tag_id
    LEFT JOIN sae.Track_Genre_Majoritaire tgm ON tgm.track_id = t.track_id
    LEFT JOIN sae.Genre gmaj ON gmaj.genre_id = tgm.genre_id
    LEFT JOIN sae.Track_Language tl ON tl.track_id = t.track_id
    LEFT JOIN sae.Language l ON tl.language_id = l.language_id
    LEFT JOIN sae.Track_Genre tg ON t.track_id = tg.track_id
    LEFT JOIN sae.Genre g ON tg.genre_id = g.genre_id
GROUP BY
    t.track_id,
    alb.album_id,
    alb.album_title,
    alb.album_handle,
    alb.album_information,
    alb.album_date_created,
    alb.album_date_released,
    alb.album_engineer,
    alb.album_producer,
    alb.album_image_file,
    a.artist_id,
    a.artist_name,
    s.track_id,
    s.danceability, 
    s.energy, 
    gmaj.genre_title,
    s.tempo,
    a.artist_location;
CREATE UNIQUE INDEX idx_view_track_mat_id ON sae.View_Track_Materialise (track_id);

CREATE OR REPLACE VIEW sae.View_Favorite_Listens AS
SELECT
    t.track_id,
    t.track_listens,
    count_favorites_track (t.track_id) as track_favorites,
    alb.album_id,
    alb.album_listens,
    count_favorites_album (alb.album_id) as album_favorites,
    p.playlist_id,
    p.playlist_listens,
    count_favorites_playlist (p.playlist_id) AS playlist_favorites
FROM
    sae.Track t
    JOIN sae.Artist_Album_Track aat ON t.track_id = aat.track_id
    JOIN sae.Album alb ON aat.album_id = alb.album_id
    LEFT JOIN sae.Playlist_Track pt ON pt.track_id = t.track_id
    LEFT JOIN sae.Playlist p ON pt.playlist_id = p.playlist_id
GROUP BY
    t.track_id,
    t.track_listens,
    alb.album_id,
    alb.album_listens,
    p.playlist_id,
    p.playlist_listens;

CREATE OR REPLACE VIEW sae.view_user_permissions AS
SELECT 
    u.user_id,
    u.pseudo,
    r.role_name,
    p.permission_label
FROM sae.User u
JOIN sae.User_Role ur ON u.user_id = ur.user_id
JOIN sae.Role r ON ur.role_id = r.role_id
JOIN sae.Role_Permission rp ON r.role_id = rp.role_id
JOIN sae.Permission p ON rp.permission_id = p.permission_id;