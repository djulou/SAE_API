import { useState, useEffect } from "react"
import type { Page } from "./types/Page"
import "./cookie_wall.css"

type CookieProps = {
    onNavigate: (page: Page) => void
}

export default function ConsentPopup({ onNavigate }: CookieProps) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const consent = localStorage.getItem("consent")

    if (!consent) {
        setVisible(true)
    }
  }, [])

  function handleYes () {
    localStorage.setItem("consent", "yes")
    setVisible(false)
    onNavigate("register")
  }

  function handleNo() {
    localStorage.setItem("consent", "no")
  }

  if (!visible) {return null}

  return (
    <div className="overlay">
      <div className="popup">
        <h2>Acceptez-vous l'utilisation de cookies ?</h2>
        <p>Ce site nécessite de pouvoir accéder aux données de l'utilisateur afin de fonctionner, 
            ceci afin de pouvoir offrir une expérience plus personnalisée et réactive aux actions de l'utilisateur</p>

        <div className="button-container">
          <button className="buttons" onClick={() => handleYes()}>J'accepte</button>
          <button className="buttons" onClick={() => handleNo()}>Je refuse</button>
        </div>
      </div>
    </div>
  );
}