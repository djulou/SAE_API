import coeur from "../assets/coeur.png"
import playlist from "../assets/playlist.png"


type Track = {
    user_id: number
    track_id: number
    nb_listening: number
}

type Genre = {
    user_id: number
    genre_id: number
    genre_rate: number
}

type StatsUserProps = {
    favoris: number
    playlists: number
    track_listen: Track[]
    genre_listen: Genre[]
}


function StatsUser({favoris, playlists, track_listen, genre_listen}: StatsUserProps) {
    return (
        <section>
            <div className="stats" >
                <div className="stat-simple">
                    <h2 className="souligner">Nombre de musique en favoris : </h2>
                    <div className="chiffre-image">
                        <p className="chiffre-stat">{favoris}</p>
                        {/* <img src={coeur} id="image-favoris" alt="Image favoris"></img> */}
                    </div>
                </div>
                <div className="stat-simple">
                    <h2 className="souligner">Nombre de playlists créées : </h2>
                    <div className="chiffre-image">
                        <p className="chiffre-stat">{playlists}</p>
                        {/* <img src={playlist} id="image-playlist" alt="Image playlist"></img> */}
                    </div>
                </div>
            </div>
        <div className="stats">
            <div className="stat-graph">
                <h2 className="souligner">Artistes les plus écoutés : </h2>
            </div>
            <div className="stat-graph"> 
                <h2 className="souligner">Genres les plus écoutés : </h2>
            </div>
        </div>
        </section>
    )
}

export default StatsUser
