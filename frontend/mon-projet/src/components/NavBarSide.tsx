import { deletePlaylist } from "../services/playlistService"
import type { Page } from "../types/Page"
import poubelleIcon from "../assets/poubelle.png"


import "../index.css"

type NavBarProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
  setModalOpen: (open: boolean) => void
  onOpenPlaylist: (id: number) => void
  setSelectedTrackId: (id: number | null) => void
  userPlaylists: PlaylistDB[]
  onPlaylistDeleted?: () => void
}


interface PlaylistDB {
  playlist_id: number;
  playlist_name: string;
  playlist_listens?: number;
  user_id?: number;
}

function NavBarSide({ onNavigate, isConnected, setModalOpen, onOpenPlaylist, setSelectedTrackId, userPlaylists, onPlaylistDeleted }: NavBarProps) {

  const handleDelete = async (id: number, name: string) => {
    if (window.confirm(`Voulez-vous vraiment supprimer la playlist "${name}" ?`)) {
      try {
        await deletePlaylist(id);
        if (onPlaylistDeleted) onPlaylistDeleted();
      } catch (err: any) {
        alert(err.message);
      }
    }
  };


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
                style={{ cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}
                onClick={() => onOpenPlaylist(pl.playlist_id)}
              >
                <span>{pl.playlist_name}</span>
                <button
                  className="btn-delete-playlist-mini"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(pl.playlist_id, pl.playlist_name);
                  }}
                  title="Supprimer la playlist"
                >
                  <img src={poubelleIcon} alt="Supprimer" width="16" height="16" style={{ display: 'block', pointerEvents: 'none' }} />
                </button>



              </li>
            ))}

          </ul>
        )}
      </div>
    </nav>
  )
}

export default NavBarSide