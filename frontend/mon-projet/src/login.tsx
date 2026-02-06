// import "./Login.css"

type LoginProps = {
  onLogin: () => void
  onRegister: () => void
}

function Login({ onLogin, onRegister }: LoginProps): JSX.Element {
  return (
    <div className="login-page">
      <div className="login-container">
        <h1 className="login-title">Connexion à Orchestra</h1>

        <div className="login-form">
          <div>
            <label>Votre adresse mail</label>
            <input
              type="email"
              placeholder="Renseignez une adresse mail"
            />
          </div>

          <div>
            <label>Votre mot de passe</label>
            <input
              type="password"
              placeholder="Renseignez un mot de passe"
            />
          </div>
        </div>

        <div className="login-actions">
          <button className="btn confirm" onClick={onLogin}>
            Confirmer
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
