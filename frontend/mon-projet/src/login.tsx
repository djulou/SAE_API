// import "./Login.css"
import { useState } from "react"
import { login } from "./services/authService"

type LoginProps = {
  onLogin: () => void
  onRegister: () => void
}

function Login({ onLogin, onRegister }: LoginProps) {
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async () => {
    if (!username || !password) {
      setError("Veuillez remplir tous les champs")
      return
    }

    setIsLoading(true)
    setError("")

    try {
      await login(username, password)
      onLogin()
    } catch (err: any) {
      setError(err.message || "Identifiants incorrects")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <h1 className="login-title">Connexion à Orchestra</h1>

        <div className="login-form">
          {error && <div style={{ color: "var(--color-danger)", textAlign: "center", marginBottom: "1rem" }}>{error}</div>}

          <div>
            <label>Votre pseudo ou email</label>
            <input
              type="text"
              placeholder="Renseignez votre identifiant"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
          </div>

          <div>
            <label>Votre mot de passe</label>
            <input
              type="password"
              placeholder="Renseignez un mot de passe"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
            />
          </div>
        </div>

        <div className="login-actions">
          <button
            className="btn confirm"
            onClick={handleSubmit}
            disabled={isLoading}
          >
            {isLoading ? "Chargement..." : "Confirmer"}
          </button>

          <button className="btn cancel" onClick={onRegister}>
            S’inscrire
          </button>
        </div>

        <div className="contact">
          Un problème ? Contactez-nous !
        </div>
      </div>
    </div>
  )
}

export default Login
