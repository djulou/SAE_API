
import CarteChanson from './components/carte_chanson'
import viteLogo from '/vite.svg'

export default
function Accueil() {
    return (
        <>
            <h2>Musique recommandées</h2>
	<div className="grille-carte-chanson">
		
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
	</div>
	<h2>Playlist recommandées</h2>
	<div className="grille-carte-chanson">
		
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
	</div>
	<h2>album recommandées</h2>
	<div className="grille-carte-chanson">
		
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
		<CarteChanson
			title="Let It Go"
			artist="Idina Menzel"
			pochette={viteLogo}
		/>
	</div>
            </>
        )
    }
