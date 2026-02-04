
type Page = 'acceuil' | 'detail_compte'
type HeaderProps = {
  onNavigate: (page: Page) => void
}

export default function Footer({ onNavigate }: HeaderProps): JSX.Element {
  return (
    <footer className="footer">
      <nav className="footer-links">
        <a href="/cgu">CGU</a>
        <a href="/contact">Contact</a>
        <a href="/mentions-legales">Mentions légales</a>
      </nav>

      <p className="footer-copy">
        © Tous droits réservés
      </p>
    </footer>
  )
}
