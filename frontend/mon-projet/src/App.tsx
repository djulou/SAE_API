import { useState } from "react"
import "./App.css"
import "./index.css"

import Header from "./components/Header"
import Footer from "./components/Footer"

import Accueil from "./accueil"
import DetailCompte from "./detail_compte"
import PageInstallation from "./installation"
import Login from "./login"
import Register from "./register"


import type { Page } from "./types/Page"

// type Page =
//   | "acceuil"
//   | "detail_compte"
//   | "page_installation"
//   | "login"
//   | "register"

function App(): JSX.Element {
  const [page, setPage] = useState<Page>("acceuil")

  // 🔐 état de connexion
  const [isConnected, setIsConnected] = useState<boolean>(false)

  return (
    <>
      <Header onNavigate={setPage} isConnected={isConnected} />

      {page === "acceuil" && <Accueil isConnected= {isConnected} />}

      {page === "detail_compte" && (
        isConnected ? <DetailCompte /> : setPage("login")
      )}

      {page === "page_installation" && <PageInstallation />}

      {page === "login" && (
        <Login
          onLogin={() => {
            setIsConnected(true)
            setPage("acceuil")
          }}
          onRegister={() => setPage("register")}
        />
      )}

      {page === "register" && (
        <Register
          onRegister={() => {
            setIsConnected(true)
            setPage("acceuil")
          }}
          onCancel={() => setPage("login")}
        />
      )}

      <Footer onNavigate={setPage} />
    </>
  )
}

export default App
