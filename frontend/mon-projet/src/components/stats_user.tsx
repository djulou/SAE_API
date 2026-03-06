import { useState, useEffect } from "react";
import coeur from "../assets/coeur.png";
import playlistIcon from "../assets/playlist.png";
import "./stats_user.css";

// --- TYPES ---
type TopTrack = {
    track_id: number;
    track_title: string;
    nb_listening: number;
    track_genre?: string; // Ajout du genre récupéré via la track
};

type TopGenre = {
    genre_id: number;
    genre_title: string;
    genre_rate: number;
};

type UserCounts = {
    favoris: number;
    playlists: number;
};

function StatsUser() {
    const [counts, setCounts] = useState<UserCounts>({ favoris: 0, playlists: 0 });
    const [topTracks, setTopTracks] = useState<TopTrack[]>([]);
    const [topGenres, setTopGenres] = useState<TopGenre[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAllStats = async () => {
            setLoading(true);
            const token = localStorage.getItem("token");
            const headers = { Authorization: `Bearer ${token}` };

            try {
                const [resCounts, resTracks, resGenres] = await Promise.all([
                    fetch("http://127.0.0.1:8000/stats/user/counts", { headers }),
                    fetch("http://127.0.0.1:8000/stats/user/top-tracks", { headers }),
                    fetch("http://127.0.0.1:8000/stats/user/top-genres", { headers })
                ]);

                if (resCounts.ok) setCounts(await resCounts.json());
                if (resTracks.ok) setTopTracks(await resTracks.json());
                if (resGenres.ok) setTopGenres(await resGenres.json());
            } catch (err) {
                console.error("Erreur lors du chargement des statistiques:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchAllStats();
    }, []);

    const maxListens = topTracks.length > 0 ? Math.max(...topTracks.map(t => t.nb_listening)) : 1;

    if (loading) return <div className="loading-stats">Chargement de vos statistiques...</div>;

    return (
        <section className="stats-section">
            <div className="stats-grid-top">
                <div className="stat-card-mini">
                    <img src={coeur} className="stat-icon" alt="Favoris" />
                    <div className="stat-info">
                        <span className="stat-label">Titres Aimés</span>
                        <p className="stat-value">{counts.favoris}</p>
                    </div>
                </div>
                
                <div className="stat-card-mini">
                    <img src={playlistIcon} className="stat-icon" alt="Playlists" />
                    <div className="stat-info">
                        <span className="stat-label">Mes Playlists</span>
                        <p className="stat-value">{counts.playlists}</p>
                    </div>
                </div>
            </div>

            <div className="stats-grid-bottom">
                <div className="stat-card-large">
                    <h3 className="stat-title">Titres les plus écoutés</h3>
                    <ul className="visual-list">
                        {topTracks.length > 0 ? (
                            topTracks.map((track) => (
                                <li key={track.track_id} className="visual-item">
                                    <div className="item-text">
                                        <div className="item-main-info">
                                            <span className="item-name">{track.track_title}</span>
                                            {/* On affiche le genre ici */}
                                            <span className="item-sub-genre">{track.track_genre || "Genre inconnu"}</span>
                                        </div>
                                        <span className="item-count">{track.nb_listening} écoutes</span>
                                    </div>
                                    <div className="progress-bar-bg">
                                        <div 
                                            className="progress-fill track-fill" 
                                            style={{ width: `${(track.nb_listening / maxListens) * 100}%` }}
                                        ></div>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <p className="empty-msg">Aucune écoute enregistrée pour le moment.</p>
                        )}
                    </ul>
                </div>

                <div className="stat-card-large">
                    <h3 className="stat-title">Genres préférés</h3>
                    <ul className="visual-list">
                        {topGenres.length > 0 ? (
                            topGenres.map((genre) => (
                                <li key={genre.genre_id} className="visual-item">
                                    <div className="item-text">
                                        <span className="item-name">{genre.genre_title}</span>
                                        <span className="item-count">{(genre.genre_rate * 100).toFixed(0)}%</span>
                                    </div>
                                    <div className="progress-bar-bg">
                                        <div 
                                            className="progress-fill genre-fill" 
                                            style={{ width: `${genre.genre_rate * 100}%` }}
                                        ></div>
                                    </div>
                                </li>
                            ))
                        ) : (
                            <p className="empty-msg">Écoutez plus de musique pour définir votre profil.</p>
                        )}
                    </ul>
                </div>
            </div>
        </section>
    );
}

export default StatsUser;