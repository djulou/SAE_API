import { useState } from 'react'
import Coeur from "./coeur"
import plus from "../assets/plus.svg"

type CarteChansonProps = {
  title: string
  artist: string
  pochette: string
  isConnected: boolean
  onAdd?: () => void
}

function CarteChanson({
  title,
  artist,
  pochette,
  isConnected,
  onAdd
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

        <div className="actions-overlay">
          <Coeur
            isFavorite={isFavorite}
            isConnected={isConnected}
            toggleFavorite={toggleFavorite}
          />
        </div>
      </div>

      <article className="description">
        <div>
          <h3>{title}</h3>
          <p>{artist}</p>
        </div>
        {isConnected && onAdd && (
          <button
            className="btn-plus"
            onClick={(e) => {
              e.stopPropagation();
              onAdd();
            }}
            title="Ajouter à une playlist"
          >
            <img src={plus} alt="Ajouter" style={{ width: "30px", height: "30px" }} />
          </button>
        )}
      </article>
    </div>
  )
}

export default CarteChanson
