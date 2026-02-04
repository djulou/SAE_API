type CarteChansonProps = {
  title: string
  artist: string
  pochette: string
}

function CarteChanson({ title, artist, pochette }: CarteChansonProps) {
  return (
	<> 
    <div className="carte-chanson">
      <div className="pochette-wrapper">
          <img
          src={pochette}
          alt={`Pochette de ${title}`}
          className="pochette"/>
      </div>

      <div className="description">
          <h3>{title}</h3>
          <p>{artist}</p>
      </div>
    </div>
	</>
  

  )
}

export default CarteChanson
