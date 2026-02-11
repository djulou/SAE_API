import { useState, useEffect } from "react"
// import "./App.css"
import "./index.css"

import Header from "./components/Header"
import Footer from "./components/Footer"

import Accueil from "./accueil"
import DetailCompte from "./detail_compte"
import PageInstallation from "./installation"
import Login from "./login"
import Register from "./register"
import { getCurrentUser, logout } from "./services/authService"


import type { Page } from "./types/Page"

function App() {
  const [page, setPage] = useState<Page>("accueil")

  // 🔐 état de connexion
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [userId, setUserId] = useState<number | null>(null)

  // Vérification de la session au chargement
  useEffect(() => {
    const token = localStorage.getItem("token")
    if (token) {
      getCurrentUser()
        .then(user => {
          setIsConnected(true)
          setUserId(user.user_id)
        })
        .catch(() => {
          logout()
          setIsConnected(false)
        })
    }
  }, [])

  const handleLoginSuccess = () => {
    setIsConnected(true)
    const storedId = localStorage.getItem("user_id")
    if (storedId) setUserId(parseInt(storedId))
    setPage("accueil")
  }

  const handleLogout = () => {
    logout()
    setIsConnected(false)
    setUserId(null)
    setPage("accueil")
  }

  return (
    <>
      <Header onNavigate={setPage} isConnected={isConnected} onLogout={handleLogout} />

      {page === "accueil" && <Accueil isConnected={isConnected} userId={userId} />}

      {page === "detail_compte" && (
        isConnected ? <DetailCompte /> : setPage("login")
      )}

      {page === "page_installation" && <PageInstallation />}

      {page === "login" && (
        <Login
          onLogin={handleLoginSuccess}
          onRegister={() => setPage("register")}
        />
      )}

      {page === "register" && (
        <Register
          onNavigate={setPage}
        />
      )}

      <Footer onNavigate={setPage} />
    </>
  )
}

export default App
