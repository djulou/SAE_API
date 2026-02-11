type Page = 'accueil' | 'detail_compte' | 'CGU' | 'contact' | 'mentions_legales'
type HeaderProps = {

type Page = 'accueil' | 'detail_compte' | 'page_installation' | 'login' | 'register'
type FooterProps = {
  onNavigate: (page: Page) => void
}

function Footer({ onNavigate }: HeaderProps): JSX.Element {
  return (
    <footer className="footer">
      <nav className="footer-links">
        <button onClick={() => {window.scrollTo({ top: 0, left: 0}), onNavigate("CGU")}}>CGU</button>
        <button onClick={() => onNavigate("contact")}>Contact</button>
        <button onClick={() => {window.scrollTo({ top: 0, left: 0}), onNavigate("mentions_legales")}}>Mentions Légales</button>
      </nav>

      <p className="footer-copy">
        © Tous droits réservés
      </p>
    </footer>
  )
}

export default Footer
