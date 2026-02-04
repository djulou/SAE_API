import "./user.css"
import InfoUser from "./components/info_user";

export default

function detail_compte() {
    return (
        <>
            <InfoUser
                email="adressemail@truc.com"
                id="ncxjfvdst"
                password="motdepass123"
            />

            <button id="bouton-user" className="bouton-cliquable">Afficher stats utilisateurs</button>

            <div>
                <button id="deconnecter" className="bouton-cliquable">Se déconnecter</button>
                <button id="supprimer" className="bouton-cliquable">Supprimer le compte</button>
            </div>
        </>
    );
}
