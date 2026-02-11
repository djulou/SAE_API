type Page = 'acceuil' | 'detail_compte' | 'CGU' | 'contact' | 'mentions_legales'
type HeaderProps = {
  onNavigate: (page: Page) => void
}

function Footer({ onNavigate }: HeaderProps): JSX.Element {
  return (
    <footer className="footer">
      <nav className="footer-links">
        <button onClick={() => onNavigate("CGU")}>CGU</button>
        <button onClick={() => onNavigate("contact")}>Contact</button>
        <button onClick={() => onNavigate("mentions_legales")}>Mentions Légales</button>
      </nav>

      <p className="footer-copy">
        © Tous droits réservés
      </p>
    </footer>
  )
}

export default Footer
