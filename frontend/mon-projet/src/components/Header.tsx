


import Logo from "../assets/logo.png"

import icon_user from "../assets/icon_user.svg"

type HeaderProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
}


function Header({ onNavigate, isConnected }: HeaderProps): JSX.Element {

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
