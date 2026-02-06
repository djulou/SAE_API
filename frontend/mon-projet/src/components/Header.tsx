import Logo from "../assets/logo.png"
import icon_user from "../assets/icon_user.svg"


type HeaderProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
}

function Header({ onNavigate, isConnected }: HeaderProps): JSX.Element {
  return (
    <header className="header">
      <button onClick={() => onNavigate("acceuil")}>
        <img src={Logo} className="logo" alt="site logo" />
      </button>

      <button onClick={() => onNavigate("page_installation")}>
        <h2>Installation</h2>
      </button>
      
      <nav>
        {!isConnected ? (
          <div className="auth-menu">
            <button onClick={() => onNavigate("login")}>Connexion</button>
            <button onClick={() => onNavigate("register")}>
              Inscription
            </button>
          </div>
        ) : (
          <button onClick={() => onNavigate("detail_compte")}>
            <img
              src={icon_user}
              className="icon_user"
              alt="icon utilisateur"
            />
          </button>
        )}
      </nav>
    </header>
  )
}

export default Header
