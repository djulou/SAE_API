

import { useState } from 'react'
import './App.css'
import './index.css'

import Header from './components/Header'
import Accueil from './accueil'
import DetailCompte from './detail_compte'

type Page = 'acceuil' | 'detail_compte'

function App(): JSX.Element {
  const [page, setPage] = useState<Page>('acceuil')

  return (
    <>
      <Header onNavigate={setPage} />

      {page === 'acceuil' && <Accueil />}
      {page === 'detail_compte' && <DetailCompte />}
    </>
  )
}

export default App
