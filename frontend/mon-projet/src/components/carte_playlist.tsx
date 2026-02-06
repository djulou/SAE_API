import { useState } from "react"
import Coeur from "./Coeur"

type CartePlaylistProps = {
  title: string
  creator: string
  pochette: string
  isConnected: boolean
}

function CartePlaylist({
  title,
  creator,
  pochette,
  isConnected,
}: CartePlaylistProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = () => {
    setIsFavorite((prev) => !prev)
  }

  return (
    <div className="carte-playlist">
      <div className="pochette-wrapper">
        <img
          src={pochette}
          alt={`Pochette de la playlist ${title}`}
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
        <p>{creator}</p>
      </div>
    </div>
  )
}

export default CartePlaylist
