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
                <ul className="stat-list">
                    {track_listen
                        .sort((a, b) => b.nb_listening - a.nb_listening)
                        .map((track) => (
                            <li key={track.track_id}>
                                <span>Track {track.track_id}</span>
                                <span className="value">{track.nb_listening} écoutes</span>
                            </li>
                        ))
                    }
                </ul>
            </div>
            <div className="stat-graph"> 
                <h2 className="souligner">Genres les plus écoutés : </h2>
                <ul className="stat-list">
                    {genre_listen
                        .sort((a, b) => b.genre_rate - a.genre_rate)
                        .map((genre) => (
                            <li key={genre.genre_id}>
                                <span>Genre {genre.genre_id}</span>
                                <span className="value">{(genre.genre_rate * 100).toFixed(1)}%</span>
                            </li>
                        ))
                    }
                </ul>
            </div>
        </div>
        </section>
    )
}

export default StatsUser
