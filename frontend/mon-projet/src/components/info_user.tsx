import image_edit from "../assets/edit.png"

type InfoUserProps = {
  email: string
  id: string
  password: string
}

function InfoUser({email, id, password}: InfoUserProps) {
    return (
        <section className="info-user">
            <div className="principal">
                <div className="section-email">
                    <label htmlFor="email" className="titre">Adresse mail : </label>
                    <input
                        id="email"
                        type="text"
                        className="input-text"
                        value={email}
                        name="email"
                        readOnly
                    />
                    <img src={image_edit} className="image-edit" alt="Image de modification"></img>
                </div>

                <label htmlFor="id" className="titre">ID : </label>
                <input
                    id="id"
                    type="text"
                    className="input-text"
                    value={id}
                    name="id"
                    readOnly
                />
            </div>

            <div className="secondaire">
                <label htmlFor="password" className="titre">Mot de passe : </label>
                <input
                    id="password"
                    type="password"
                    className="input-text"
                    value={password}
                    name="password"
                    readOnly
                />
                <img src={image_edit} className="image-edit" alt="Image de modification"></img>
            </div>
        </section>
    )
}

export default InfoUser