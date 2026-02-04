

import { useState } from 'react'
import './App.css'
import './index.css'

import Header from './components/Header'
import Footer from './components/Footer'

import Accueil from './accueil'
import DetailCompte from './detail_compte'
import page_installation from './installation'

type Page = 'acceuil' | 'detail_compte'| 'page_installation'

function App(): JSX.Element {
  const [page, setPage] = useState<Page>('acceuil')

  return (
    <>
      <Header onNavigate={setPage} />

      {page === 'acceuil' && <Accueil />}
      {page === 'detail_compte' && <DetailCompte />}
      {page === 'page_installation' && <page_installation />}
      <Footer onNavigate={setPage} />
    </>
  )
}

export default App
