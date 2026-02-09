import {useState} from "react"

import image_edit from "../assets/edit.png"
import profil from "../assets/pfp.png"

type InfoUserProps = {
  email: string
  id: string
  password: string
}


function InfoUser({email, id, password}: InfoUserProps) {
    const [emailValue, setEmailValue] = useState(email)
    const [passwordValue, setPasswordValue] = useState(password)

    const [editEmail, setEditEmail] = useState(false)
    const [editPassword, setEditPassword] = useState(false)

    return (
        <section className="info-user">
            <div className="principal">
                <img src={profil} id="image-profil" alt="Image de profil"></img>
                <div className="identification">
                    <div className="section">
                        <label htmlFor="email" className="titre"></label>
                        <input
                            id="email"
                            type="text"
                            className="input-text"
                            value={emailValue}
                            name="email"
                            readOnly={!editEmail}
                            onChange={(e) => setEmailValue(e.target.value)}
                            onBlur={() => setEditEmail(false)}
                        />
                        <img src={image_edit} id="image-edit" alt="Image de modification" onClick={() => setEditEmail(true)}></img>
                    </div>

                    <div className="section">
                        <label htmlFor="id" className="titre id"></label>
                        <input
                            id="id"
                            type="text"
                            className="input-text id"
                            value={id}
                            name="id"
                            readOnly
                        />
                    </div>
                </div>
            </div>

            <div className="secondaire">
                <div className="section">
                    <label htmlFor="password" className="titre password">Mot de passe : </label>
                    <input
                        id="password"
                        type="password"
                        className="input-text password"
                        value={passwordValue}
                        name="password"
                        readOnly={!editPassword}
                        onChange={(e) => setPasswordValue(e.target.value)}
                        onBlur={() => setEditPassword(false)}
                    />
                    <img src={image_edit} id="image-edit" alt="Image de modification" onClick={() => setEditPassword(true)}></img>
                </div>
            </div>
        </section>
    )
}

export default InfoUser
