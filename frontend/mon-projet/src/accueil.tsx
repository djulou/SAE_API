import Carousel from "./components/Carousel"
import CarteChanson from "./components/carte_chanson"
import CartePlaylist from "./components/carte_playlist"
import CarteAlbum from "./components/carte_album"
import { getChansons } from "./services/chansonService"
import type { Playlist } from "./types/Playlist"
import type { Album } from "./types/Album"
import viteLogo from "/vite.svg"

type AccueilProps = {
  isConnected: boolean
}



 
export default function Accueil( {isConnected = false} : AccueilProps)  {
  const chansons = getChansons()

  const playlists: Playlist[] = Array.from({ length: 50 }, () => ({
    title: "Top Disney",
    creator: "Orchestra",
    pochette: viteLogo,
  }))

  const albums: Album[] = Array.from({ length: 5 }, () => ({
    title: "Frozen",
    artist: "Idina Menzel",
    pochette: viteLogo,
  }))

  /* 🔎 Filtres */
  const chansonsFiltrees = chansons

  const playlistsFiltrees = playlists
  

  const albumsFiltres = albums
  

  return (
    <>


      <h2>Musiques recommandées</h2>
      <Carousel>
        {chansonsFiltrees.map((chanson, index) => (
          <CarteChanson
            key={index}
            title={chanson.title}
            artist={chanson.artist}
            pochette={chanson.pochette}
            isConnected={isConnected}
          />
        ))}
      </Carousel>

      <h2>Playlists recommandées</h2>
      <Carousel>
        {playlistsFiltrees.map((playlist, index) => (
          <CartePlaylist
            key={index}
            title={playlist.title}
            creator={playlist.creator}
            pochette={playlist.pochette}
            isConnected={isConnected}
          />
        ))}
      </Carousel>

      <h2>Albums recommandés</h2>
      <Carousel>
        {albumsFiltres.map((album, index) => (
          <CarteAlbum
            key={index}
            title={album.title}
            artist={album.artist}
            pochette={album.pochette}
            isConnected={isConnected}
          />
        ))}
      </Carousel>
    </>
  )
}
