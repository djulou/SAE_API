type CoeurProps = {
  isFavorite: boolean
  isConnected: boolean
  toggleFavorite: () => void
}

function Coeur({ isFavorite, isConnected, toggleFavorite }: CoeurProps) {
  const handleClick = () => {
    if (!isConnected) return
    toggleFavorite()
  }

  return (
    <button
      type="button"
      className={`coeur ${isFavorite ? "active" : "inactive"} ${
        !isConnected ? "disabled" : ""
      }`}
      onClick={handleClick}
      aria-label="Ajouter aux favoris"
      title={
        isConnected
          ? "Ajouter aux favoris"
          : "Connectez-vous pour ajouter aux favoris"
      }
      disabled={!isConnected}
    >
      {isFavorite ? "❤️" : "🤍"}
    </button>
  )
}

export default Coeur
