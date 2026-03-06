import { useState } from "react"
import Coeur from "./coeur"
import GeneratedCover from "./GeneratedCover"

type CarteArtistProps = {
  id?: number
  title: string
  creator: string
  isConnected: boolean
  onAdd?: () => void
  onClick?: () => void
}

function CarteArtist({
  title,
  creator,
  isConnected,
  onClick // Prop reçue
}: CarteArtistProps) {
  const [isFavorite, setIsFavorite] = useState(false)

  const toggleFavorite = (e: React.MouseEvent) => {
    e.stopPropagation(); // Évite d'ouvrir l'artiste quand on clique sur le coeur
    setIsFavorite((prev) => !prev)
  }

  return (
    <div 
      className="carte-artist" 
      onClick={onClick} // <--- AJOUTE CETTE LIGNE ICI
      style={{ cursor: "pointer" }} // Ajout d'un curseur pour indiquer que c'est cliquable
    >
      <div className="pochette-wrapper">
        <GeneratedCover title={title} />
        
        <Coeur
          isFavorite={isFavorite}
          isConnected={isConnected}
          toggleFavorite={toggleFavorite}
        />
      </div>

      <article className="description">
        <div>
          <h3>{title}</h3>
          <p>{creator}</p>
        </div>
      </article>
    </div>
  )
}

export default CarteArtist