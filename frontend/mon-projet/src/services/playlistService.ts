import type { Playlist } from "../types/Playlist"

const API_URL = "http://localhost:8000"

// Fonction utilitaire pour récupérer le token proprement
const getAuthToken = () => {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("Utilisateur non connecté");
    return token;
};

export async function getUserPlaylists(userId: number): Promise<Playlist[]> {
    const token = getAuthToken();

    const response = await fetch(`${API_URL}/users/${userId}/playlists`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Erreur API getUserPlaylists:", response.status, errorData);
        throw new Error(errorData.detail || "Impossible de récupérer les playlists");
    }
    return response.json();
}

export async function createPlaylist(title: string, userId: number): Promise<Playlist> {
    const token = getAuthToken();

    const response = await fetch(`${API_URL}/playlist`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        // On s'assure que playlist_name est une string et que user_id est bien présent
        body: JSON.stringify({ 
            playlist_name: String(title), 
            user_id: userId 
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        // Cela affichera précisément quel champ pose problème dans ta console
        console.error("Erreur API createPlaylist (422):", errorData);
        
        // Gestion propre des messages d'erreur FastAPI (qui sont souvent des listes dans 'detail')
        const message = Array.isArray(errorData.detail) 
            ? errorData.detail.map((d: any) => d.msg).join(", ") 
            : errorData.detail;
            
        throw new Error(message || "Erreur lors de la création de la playlist");
    }

    return await response.json();
}

export async function addTrackToPlaylist(playlistId: number, trackId: number): Promise<void> {
    const token = getAuthToken();

    const response = await fetch(`${API_URL}/playlistTrack`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ 
            playlist_id: Number(playlistId), 
            track_id: Number(trackId) 
        })
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error("Erreur API addTrackToPlaylist:", response.status, errorData);
        throw new Error(errorData.detail || "Impossible d'ajouter le titre à la playlist");
    }
}