import type { Page } from "../types/Page"

import "../index.css"

type NavBarProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
  setModalOpen: (open: boolean) => void
  onOpenPlaylist: (id: number) => void
  setSelectedTrackId: (id: number | null) => void
  userPlaylists: PlaylistDB[]
}

interface PlaylistDB {
  playlist_id: number;
  playlist_name: string;
  playlist_listens?: number;
  user_id?: number;
}

function NavBarSide({ onNavigate, isConnected, setModalOpen, onOpenPlaylist, setSelectedTrackId, userPlaylists }: NavBarProps) {

return (
    <nav className="menu-favoris">
        <div>
        <ul className="list-aime">
            <li onClick={() => onNavigate("albums_favorites")}>Albums favoris</li>
        </ul>

        <button
            className="btn-add-playlist"
            onClick={() => {
            setSelectedTrackId(null)
            setModalOpen(true)
            }}
        >
            Ajouter une Playlist
        </button>

        {isConnected && (
            <ul className="list-playlist">
            {userPlaylists.map((pl) => (
                <li
                key={pl.playlist_id}
                className="playlist-menu-item"
                style={{ cursor: "pointer" }}
                onClick={() => onOpenPlaylist(pl.playlist_id)}
                >
                {pl.playlist_name}
                </li>
            ))}
            </ul>
        )}
        </div>
        </nav>
    )
}

export default NavBarSide