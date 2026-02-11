
import { useState } from "react"

import Coeur from "./coeur"




type CarteAlbumProps = {
  title: string
  artist: string
  pochette: string
  isConnected: boolean

}

function CarteAlbum({ title, artist, pochette, isConnected }: CarteAlbumProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = () => {
    setIsFavorite((prev) => !prev)
  }
  return (
    <>
      <div className="carte-album" id="carte-album">
        <div className="pochette-wrapper">
          <img
            src={pochette}
            alt={`Pochette de l'album ${title}`}
            className="pochette"
          />
          <Coeur
            isFavorite={isFavorite}
            isConnected={isConnected}
            toggleFavorite={toggleFavorite}

          />
        </div>

        <div className="description">
          <h3>{title}</h3>
          <p>{artist}</p>
        </div>
      </div>
    </>
  )
}

export default CarteAlbum
