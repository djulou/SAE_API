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
import CGU from "./CGU"
import MentionsLegales from "./mentions_legales"
import Contact from "./Contact"

import PlaylistDetail from "./components/PlaylistDetail"
import AlbumDetail from "./components/AlbumDetail"
import ArtistDetail from "./components/ArtistDetail" // Ajout de l'import


import { getCurrentUser, logout } from "./services/authService"
import type { Page } from "./types/Page"

function App() {
  const [page, setPage] = useState<Page>("accueil")

  const [selectedPlaylistId, setSelectedPlaylistId] = useState<number | null>(null)
  const [selectedAlbumId, setSelectedAlbumId] = useState<number | null>(null)
  const [selectedArtistId, setSelectedArtistId] = useState<number | null>(null) // Ajout de l'état


  const [isConnected, setIsConnected] = useState<boolean>(false)
  const [userId, setUserId] = useState<number | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

    const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleLogout = () => {
    logout() 
    setIsConnected(false)
    setUserId(null)
    setPage("login") 
  }

  const handleLoginSuccess = () => {
    setIsConnected(true)
    const storedId = localStorage.getItem("user_id")
    if (storedId) setUserId(parseInt(storedId))
    setPage("accueil")
  }


  useEffect(() => {
    const verifyAuth = async () => {
      const token = localStorage.getItem("token")

      if (!token) {
        if (isConnected) setIsConnected(false)
        setIsLoading(false)
        return
      }

      try {
        // On vérifie si le token est toujours valide auprès du serveur
        const user = await getCurrentUser()
        setIsConnected(true)
        setUserId(user.user_id)
      } catch (error) {
        handleLogout()
      } finally {
        setIsLoading(false)
      }
    }

    verifyAuth()

    // Vérifie la validité toutes les 30 secondes pour rediriger automatiquement si expiration
    const interval = setInterval(verifyAuth, 30000)
    return () => clearInterval(interval)
  }, [isConnected])

  const handleOpenPlaylist = (id: number) => {
    setSelectedPlaylistId(id)
    setPage("playlist_detail")
  }

  const handleOpenAlbum = (id: number) => {
    setSelectedAlbumId(id)
    setPage("album_detail")
  }

   const handleOpenArtist = (id: number) => { // Ajout du handler
    setSelectedArtistId(id)
    setPage("artist_detail")
  }




  const renderContent = () => {
    if (isLoading) return <div className="loading">Vérification de la session...</div>

    // Protection : Si l'utilisateur tente d'accéder à "detail_compte" sans session
    if (page === "detail_compte" && !isConnected) {
      return (
        <Login
          onLogin={handleLoginSuccess}
          onRegister={() => setPage("register")}
        />
      )
    }

    switch (page) {
      case "accueil":
        return (
          <Accueil
            isConnected={isConnected}
            userId={userId}
            onOpenPlaylist={handleOpenPlaylist}
            onOpenAlbum={handleOpenAlbum}
            onOpenArtist={handleOpenArtist} // Ajout de la prop
            searchQuery={searchQuery}
          />
        )


      case "playlist_detail":
        return (
          <PlaylistDetail
            playlistId={selectedPlaylistId!}
            isConnected={isConnected}
          />
        )

      case "album_detail":
        return (
          <AlbumDetail
            albumId={selectedAlbumId!}
            isConnected={isConnected}
          />
        )

      case "artist_detail":
        return (
          <ArtistDetail
            artistId={selectedArtistId!}
            isConnected={isConnected}
          />
        )


      case "detail_compte":
        return <DetailCompte />

      case "page_installation":
        return <PageInstallation />

      case "login":
        return (
          <Login
            onLogin={handleLoginSuccess}
            onRegister={() => setPage("register")}
          />
        )

      case "register":
        return <Register onNavigate={setPage} />

      case "CGU":
        return <CGU />

      case "mentions_legales":
        return <MentionsLegales />

      case "contact":
        return <Contact onNavigate={setPage} />
      default:
        return (
          <Accueil
            isConnected={isConnected}
            userId={userId}
            onOpenPlaylist={handleOpenPlaylist}
            onOpenAlbum={handleOpenAlbum}
            onOpenArtist={handleOpenArtist}
            searchQuery={searchQuery}
          />
        )

    }
  }

  return (
    <>
      <Header
        onNavigate={setPage}
        isConnected={isConnected}
        onLogout={handleLogout}
        currentPage={page}
        onSearch={handleSearch}
      />

      <main>
        {renderContent()}
      </main>

      <Footer onNavigate={setPage} />
    </>
  )
}

export default App