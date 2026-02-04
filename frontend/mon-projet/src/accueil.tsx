import CarteChanson from './components/carte_chanson'
import CartePlaylist from './components/carte_playlist'
import CarteAlbum from './components/carte_album'
import { getChansons } from './services/chansonService'

// import type { Chanson } from './types/Chanson'
import type { Playlist } from './types/Playlist'
import type { Album } from './types/Album'

import viteLogo from '/vite.svg'

  



export default function Accueil() {
  const chansons = getChansons()


  const playlists: Playlist[] = Array.from({ length: 5 }, () => ({
    title: 'Top Disney',
    creator: 'Orchestra',
    pochette: viteLogo,
  }))

  const albums: Album[] = Array.from({ length: 5 }, () => ({
    title: 'Frozen',
    artist: 'Idina Menzel',
    pochette: viteLogo,
  }))

  return (
    <>
      <h2>Musiques recommandées</h2>
      <div className="grille-carte-chanson">
        {chansons.map((chanson, index) => (
          <CarteChanson
            key={index}
            title={chanson.title}
            artist={chanson.artist}
            pochette={chanson.pochette}
          />
        ))}
      </div>

      <h2>Playlists recommandées</h2>
      <div className="grille-carte-chanson">
        {playlists.map((playlist, index) => (
          <CartePlaylist
            key={index}
            title={playlist.title}
            creator={playlist.creator}
            pochette={playlist.pochette}
          />
        ))}
      </div>

      <h2>Albums recommandés</h2>
      <div className="grille-carte-chanson">
        {albums.map((album, index) => (
          <CarteAlbum
            key={index}
            title={album.title}
            artist={album.artist}
            pochette={album.pochette}
          />
        ))}
      </div>
    </>
  )
}
