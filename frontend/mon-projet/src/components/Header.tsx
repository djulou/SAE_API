import { useState, useRef, useEffect } from "react"
import Logo from "../assets/logo.png"
import icon_user from "../assets/icon_user.svg"
import type { Page } from "../types/Page"
import { hasRole } from "../services/authService"
import "./header.css"

type HeaderProps = {
  onNavigate: (page: Page) => void
  isConnected: boolean
  onLogout?: () => void
  currentPage: Page
  onSearch: (query: string) => void;
}

function Header({ onNavigate, isConnected, onLogout, currentPage, onSearch }: HeaderProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)
  const [tempSearch, setTempSearch] = useState("");

  // Fermer le menu si on clique en dehors
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleNavigation = (page: Page) => {
    onNavigate(page)
    setIsMenuOpen(false) // Ferme le menu après navigation
  }


  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSearch(tempSearch); // On envoie la recherche au parent
    }
  };

  return (
    <header className="header">
      <button className="button-discret" onClick={() => onNavigate("accueil")}>
        <img src={Logo} className="logo" alt="site logo" />
      </button>

      {currentPage == "accueil" && (
        <>
        <div className="search-bar">
          <input
            type="text"
            placeholder="Rechercher une musique, un artiste, une playlist..."
            value={tempSearch}
            onChange={(e) => setTempSearch(e.target.value)}
            onKeyDown={handleKeyDown}
          />
        </div>
        </>
      )}

      <nav>
        {!isConnected ? (
          <div className="auth-menu">
            <button className="btn-auth btn-login" onClick={() => onNavigate("login")}>
              Connexion
            </button>
          </div>
        ) : (
          <div className="auth-menu" ref={menuRef} style={{ position: "relative" }}>
            
            {/* Icône Utilisateur qui déclenche le menu */}
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)} 
              className="nav-button user-menu-trigger"
              style={{ background: "none", border: "none", cursor: "pointer" }}
            >
              <img
                src={icon_user}
                className="icon_user"
                alt="icon utilisateur"
                style={{ width: "32px", height: "32px" }}
              />
            </button>

            {/* Menu Déroulant */}
            {isMenuOpen && (
              <div className="dropdown-menu shadow">
                <ul className="dropdown-list">
                  <li onClick={() => handleNavigation("detail_compte")}>
                    Mon Profil
                  </li>
                  
                  {/* Option visible uniquement pour les ADMIN */}
                  {hasRole("ADMIN") && (
                    <li 
                      className="admin-option" 
                      onClick={() => handleNavigation("gestion_roles" as Page)}
                      style={{ fontWeight: "bold" }}
                    >
                      Gestion des rôles
                    </li>
                  )}

                  {hasRole("ARTIST") && (
                    <li 
                      className="artist-option" 
                      onClick={() => handleNavigation("gestion_roles" as Page)}
                      style={{ fontWeight: "bold" }}
                    >
                      Gestion du compte
                    </li>
                  )}

                  <hr />
                  
                  <li onClick={onLogout} className="logout-option">
                    Déconnexion
                  </li>
                </ul>
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  )
}

export default Header