type CartePlaylistProps = {
  title: string
  creator: string
  pochette: string
}

function CartePlaylist({ title, creator, pochette }: CartePlaylistProps) {
  return (
    <> 
      <div className="carte-chanson">
        <div className="pochette-wrapper">
          <img
            src={pochette}
            alt={`Pochette de la playlist ${title}`}
            className="pochette"
          />
        </div>

        <div className="description">
          <h3>{title}</h3>
          <p>{creator}</p>
        </div>
      </div>
    </>
  )
}

export default CartePlaylist
