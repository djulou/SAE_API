import Logo from "../assets/logo.png"
import icon_user from "../assets/icon_user.svg"


type Page = 'acceuil' | 'detail_compte'

type HeaderProps = {
  onNavigate: (page: Page) => void
}

function Header({ onNavigate }: HeaderProps): JSX.Element {
  return (
    <header className="header">
      <button onClick={() => onNavigate('acceuil')}>
        <img src={Logo} className="logo" alt="site logo" />
      </button>
      <h1>Mon App</h1>

      <nav>

        <button onClick={() => onNavigate('detail_compte')}>
          <img src={icon_user} className="icon_user" alt="icon_user" />
          {/* Détail compte */}
        </button>
      </nav>
    </header>
  )
}

export default Header
