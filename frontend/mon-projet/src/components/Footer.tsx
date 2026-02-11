
type Page = 'accueil' | 'detail_compte' | 'page_installation' | 'login' | 'register'
type FooterProps = {
  onNavigate: (page: Page) => void
}

export default function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="footer">
      <div className="footer-links">
        <a href="#" onClick={(e) => { e.preventDefault(); onNavigate('accueil'); }}>Accueil</a>
        <a href="/mentions-legales">Mentions légales</a>
      </div>

      <p className="footer-copy">
        © Tous droits réservés
      </p>
    </footer>
  )
}
