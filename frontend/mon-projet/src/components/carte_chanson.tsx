import { useState } from 'react'
import Coeur from "./Coeur"

type CarteChansonProps = {
  title: string
  artist: string
  pochette: string
  isConnected: boolean
}

function CarteChanson({
  title,
  artist,
  pochette,
  isConnected,
}: CarteChansonProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = () => {
    if (!isConnected) return
    setIsFavorite(prev => !prev)
  }

  return (
    <div className="carte-chanson">
      <div className="pochette-wrapper">
        <img
          src={pochette}
          alt={`Pochette de ${title}`}
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
  )
}

export default CarteChanson
