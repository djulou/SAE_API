import Logo from "../assets/logo.png"
import icon_user from "../assets/icon_user.svg"
import type { Page } from "../types/Page"

type HeaderProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
  onLogout?: () => void
}


function Header({ onNavigate, isConnected, onLogout }: HeaderProps) {

  return (
    <header className="header">
      <button onClick={() => onNavigate("accueil")}>
        <img src={Logo} className="logo" alt="site logo" />
      </button>
      {/* 🔍 BARRE DE RECHERCHE */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Rechercher une musique, un artiste, une playlist..."
        // value={search}
        // onChange={(e) => setSearch(e.target.value)}
        />
      </div>
      <button
        className="nav-button"
        onClick={() => onNavigate("page_installation")}
      >
        Installation
      </button>


      <nav>
        {!isConnected ? (
          <div className="auth-menu">
            <button
              className="btn-auth btn-login"
              onClick={() => onNavigate("login")}
            >
              Connexion
            </button>

            <button
              className="btn-auth btn-register"
              onClick={() => onNavigate("register")}
            >
              Inscription
            </button>
          </div>

        ) : (
          <div className="auth-menu">
            <button onClick={() => onNavigate("detail_compte")} className="nav-button">
              <img
                src={icon_user}
                className="icon_user"
                alt="icon utilisateur"
                style={{ width: "32px", height: "32px" }}
              />
            </button>
            <button onClick={onLogout} className="btn-auth btn-login" style={{ marginLeft: "10px" }}>
              Déconnexion
            </button>
          </div>
        )}
      </nav>
    </header>
  )
}

export default Header
