import type { Page } from "../types/Page"

type FooterProps = {
  onNavigate: (page: Page) => void
}

function Footer({ onNavigate }: FooterProps) {
  return (
    <footer className="footer">
      <nav className="footer-links">
        <button onClick={() => { window.scrollTo({ top: 0, left: 0 }); onNavigate("CGU") }}>CGU</button>
        <button onClick={() => { window.scrollTo({ top: 0, left: 0 }); onNavigate("mentions_legales") }}>Mentions Légales</button>
      </nav>

      <p className="footer-copy">
        © Tous droits réservés
      </p>
    </footer>
  )
}

export default Footer
