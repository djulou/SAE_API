import { useState } from 'react'
<<<<<<< HEAD
import Coeur from "./coeur"
=======
import Coeur from "./Coeur"
import plus from "../assets/plus.svg"

>>>>>>> 17c9aff0ba654f7c639f3b698b8fececb252ef52

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
          {isConnected && onAdd && (
            <button
              className="btn-add-track"
              onClick={(e) => {
                e.stopPropagation();
                onAdd();
              }}
              title="Ajouter à une playlist"
            >
              +
            </button>
          )}
        </div>
      </div>
  
      	<article className="description">
        	<div>
          		<h3>{title}</h3>
        		<p>{artist}</p>
        	</div>
			<button
				className="btn-plus"
				onClick={() => console.log("Ajouter à la playlist")}
				>
				<svg
					xmlns="http://www.w3.org/2000/svg"
					width="30"
					height="30"
					viewBox="0 0 24 24"
					stroke="currentColor"
					strokeWidth="2.75"
					strokeLinecap="round"
					strokeLinejoin="round"
				>
					<path d="M5 12h14" />
					<path d="M12 5v14" />
				</svg>
				</button>

     	 			</article>
    </div>
  )
}

export default CarteChanson
