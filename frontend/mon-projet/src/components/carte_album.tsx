type CarteAlbumProps = {
  title: string
  artist: string
  pochette: string
}

function CarteAlbum({ title, artist, pochette }: CarteAlbumProps) {
  return (
    <>
      <div className="carte-chanson">
        <div className="pochette-wrapper">
          <img
            src={pochette}
            alt={`Pochette de l'album ${title}`}
            className="pochette"
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
