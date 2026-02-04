import "./user.css"
import InfoUser from "./components/info_user";

export default

function detail_compte() {
    return (
        <>
            <div>
                <h2>Détail du Compte</h2>
                <p>Informations détaillées sur le compte utilisateur.</p>
            </div>

            <InfoUser
                email="adressemail@truc.com"
                id="ncxjfvdst"
                password="motdepass123"
            />

            <button id="bouton-user">Afficher stats utilisateurs</button>

            <div>
                <button id="deconnecter">Se déconnecter</button>
                <button id="supprimer">Supprimer le compte</button>
            </div>
        </>
    );
}
