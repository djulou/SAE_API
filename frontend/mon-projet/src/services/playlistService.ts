import type { Playlist } from "../types/Playlist"

const API_URL = "http://localhost:8000"

export async function getUserPlaylists(userId: number): Promise<Playlist[]> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("Utilisateur non connecté")

    const response = await fetch(`${API_URL}/users/${userId}/playlists`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Erreur API getUserPlaylists:", response.status, errorData);
        throw new Error(errorData.detail || "Impossible de récupérer les playlists");
    }
    return response.json()
}

export async function createPlaylist(userId: number, title: string): Promise<Playlist> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("Utilisateur non connecté")

    const response = await fetch(`${API_URL}/playlist`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ playlist_name: title })
    })

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Erreur API createPlaylist:", response.status, errorData);
        throw new Error(errorData.detail || "Erreur lors de la création de la playlist");
    }

    // Si l'API ne lie pas automatiquement la playlist au user à la création (ce qui est souvent le cas en REST pur),
    // il faudrait peut-être faire un appel supplémentaire, mais ici on suppose que le backend gère le user_id via le token ou le body si besoin.
    // D'après ta route create_playlist dans main.py : elle prend le user_id du token (current_user).

    const newPlaylist = await response.json()

    // Il faut aussi créer le lien dans PlaylistUser si ce n'est pas fait auto par le backend, 
    // mais regardons ton backend : create_playlist fait `new_playlist = Playlist(..., user_id=current_user.user_id)`.
    // Donc c'est bon, la playlist appartient bien au user.

    return newPlaylist
}

export async function addTrackToPlaylist(playlistId: number, trackId: number): Promise<void> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("Utilisateur non connecté")

    // POST /playlistTrack
    // Body: { playlist_id: int, track_id: int }
    const response = await fetch(`${API_URL}/playlistTrack`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ playlist_id: playlistId, track_id: trackId })
    })

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Erreur API addTrackToPlaylist:", response.status, errorData);
        throw new Error(errorData.detail || "Impossible d'ajouter le titre à la playlist");
    }
}
