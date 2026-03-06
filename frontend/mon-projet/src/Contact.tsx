import { useState } from "react"
import type { Page } from "./types/Page"


type ContactProps = {
  onNavigate: (page: Page) => void
}

function Contact({ onNavigate }: ContactProps) {
  const [email, setEmail] = useState("")
  const [subject, setSubject] = useState("")
  const [message, setMessage] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!email || !subject || !message) {
      setError("Veuillez remplir tous les champs")
      return
    }

    setError("")
    setSuccess("")
    setIsLoading(true)

    try {
      setSuccess("Message envoyé avec succès !")

      setEmail("")
      setSubject("")
      setMessage("")
    } catch (err: any) {
      setError("Impossible d'envoyer le message")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <h1 className="login-title">Contact</h1>

        <div className="login-form">
          {error && (
            <div
              style={{
                color: "var(--color-danger)",
                textAlign: "center",
                marginBottom: "1rem"
              }}
            >
              {error}
            </div>
          )}

          {success && (
            <div
              style={{
                color: "var(--color-success)",
                textAlign: "center",
                marginBottom: "1rem"
              }}
            >
              {success}
            </div>
          )}

          <label>Votre email</label>
          <input
            className="champ"
            type="email"
            placeholder="Renseignez votre email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label>Sujet</label>
          <input
            className="champ"
            type="text"
            placeholder="Sujet du message"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />

          <label>Votre message</label>
          <textarea
            className="champ"
            placeholder="Écrivez votre message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            rows={5}
          />
        </div>

        <div className="login-actions">
          <button
            className="btn confirm"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Envoi..." : "Envoyer"}
          </button>

          <button className="btn cancel" onClick={() => onNavigate("accueil")}>
            Retour
          </button>
        </div>

        <div className="contact">
          Nous vous répondrons dès que possible.
        </div>
      </div>
    </div>
  )
}

export default Contact