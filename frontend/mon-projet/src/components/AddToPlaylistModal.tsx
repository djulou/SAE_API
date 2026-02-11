import { useState, useEffect } from "react";
import { getUserPlaylists, createPlaylist, addTrackToPlaylist } from "../services/playlistService";
import type { Playlist } from "../types/Playlist";

interface AddToPlaylistModalProps {
    isOpen: boolean;
    onClose: () => void;
    trackId: number | null;
    userId: number | null;
}

export default function AddToPlaylistModal({ isOpen, onClose, trackId, userId }: AddToPlaylistModalProps) {
    const [playlists, setPlaylists] = useState<Playlist[]>([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedPlaylistIds, setSelectedPlaylistIds] = useState<number[]>([]);
    const [loading, setLoading] = useState(false);
    const [creating, setCreating] = useState(false);
    const [newPlaylistName, setNewPlaylistName] = useState("");

    // Charger les playlists à l'ouverture
    useEffect(() => {
        if (isOpen && userId) {
            setLoading(true);
            getUserPlaylists(userId)
                .then(setPlaylists)
                .catch(console.error)
                .finally(() => setLoading(false));
        }
    }, [isOpen, userId]);

    if (!isOpen) return null;

    const filteredPlaylists = playlists.filter((p) => {
        const name = p.playlist_name || p.title || "";
        return name.toLowerCase().includes(searchQuery.toLowerCase());
    });

    const toggleSelection = (id: number) => {
        setSelectedPlaylistIds((prev) =>
            prev.includes(id) ? prev.filter((pid) => pid !== id) : [...prev, id]
        );
    };

    const handleCreatePlaylist = async () => {
        if (!newPlaylistName.trim() || !userId) return;
        try {
            const newPlaylist = await createPlaylist(userId, newPlaylistName);
            setPlaylists((prev) => [...prev, newPlaylist]);
            setSelectedPlaylistIds((prev) => [...prev, newPlaylist.playlist_id]); // Auto-select
            setCreating(false);
            setNewPlaylistName("");
        } catch (err: any) {
            console.error("Erreur création playlist:", err);
            alert(err.message || "Erreur lors de la création de la playlist");
        }
    };

    const handleSave = async () => {
        if (!trackId) return;

        // Pour chaque playlist sélectionnée, on ajoute le titre
        // Idéalement, on devrait faire ça en parallèle avec Promise.all
        try {
            const promises = selectedPlaylistIds.map(pid => addTrackToPlaylist(pid, trackId));
            await Promise.all(promises);
            alert("Titre ajouté aux playlists !");
            onClose();
            setSelectedPlaylistIds([]); // Reset selection
        } catch (err: any) {
            console.error("Erreur ajout playlist:", err);
            alert(err.message || "Une erreur est survenue lors de l'ajout.");
        }
    };

    return (
        <div className="modal-overlay">
            <div className="modal-content">
                <div className="modal-header">
                    <h2>{trackId ? "Ajouter à une playlist" : "Gérer mes playlists"}</h2>
                    <button onClick={onClose} className="close-btn">&times;</button>
                </div>

                <div className="modal-body">
                    {/* Barre de recherche */}
                    <input
                        type="text"
                        placeholder="Rechercher une playlist..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="search-input"
                    />

                    {/* Liste des playlists */}
                    <div className="playlist-list">
                        {loading ? (
                            <p>Chargement...</p>
                        ) : filteredPlaylists.length > 0 ? (
                            filteredPlaylists.map((playlist) => (
                                <div key={playlist.playlist_id} className="playlist-item">
                                    <label>
                                        <input
                                            type="checkbox"
                                            checked={selectedPlaylistIds.includes(playlist.playlist_id)}
                                            onChange={() => toggleSelection(playlist.playlist_id)}
                                        />
                                        <span className="playlist-name">{playlist.playlist_name || playlist.title || "Sans titre"}</span>
                                        <span className="playlist-count">({playlist.tracks?.length || 0} titres)</span>
                                    </label>
                                </div>
                            ))
                        ) : (
                            <p className="no-result">Aucune playlist trouvée.</p>
                        )}
                    </div>

                    {/* Section Création */}
                    {creating ? (
                        <div className="create-section">
                            <input
                                type="text"
                                placeholder="Nom de la playlist"
                                value={newPlaylistName}
                                onChange={(e) => setNewPlaylistName(e.target.value)}
                                autoFocus
                            />
                            <button
                                className="btn-primary-small"
                                onClick={handleCreatePlaylist}
                                disabled={!newPlaylistName.trim()}
                            >
                                OK
                            </button>
                            <button className="btn-cancel-small" onClick={() => setCreating(false)}>Annuler</button>
                        </div>
                    ) : (
                        <button className="btn-create-playlist" onClick={() => setCreating(true)}>
                            + Créer une nouvelle playlist
                        </button>
                    )}
                </div>

                <div className="modal-footer">
                    <button className="btn-cancel" onClick={onClose}>Annuler</button>
                    <button
                        className="btn-confirm"
                        onClick={handleSave}
                        disabled={selectedPlaylistIds.length === 0}
                    >
                        Ajouter
                    </button>
                </div>
            </div>
        </div>
    );
}
