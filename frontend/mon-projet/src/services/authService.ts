const API_URL = "http://localhost:8000"

export type UserProfile = {
    user_id: number
    user_login: string
    pseudo: string
    email: string
    image?: string
}

export async function login(username: string, password: string) {
    const formData = new FormData()
    formData.append("username", username)
    formData.append("password", password)

    const response = await fetch(`${API_URL}/login`, {
        method: "POST",
        body: formData,
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || "Échec de la connexion")
    }

    const data = await response.json()
    localStorage.setItem("token", data.access_token)

    // On récupère les infos du user pour avoir son ID
    const userProfile = await getCurrentUser()
    localStorage.setItem("user_id", userProfile.user_id.toString())

    return { token: data.access_token, user: userProfile }
}

export async function getCurrentUser(): Promise<UserProfile> {
    const token = localStorage.getItem("token")
    if (!token) throw new Error("Non authentifié")

    const response = await fetch(`${API_URL}/user`, {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    })

    if (!response.ok) {
        localStorage.removeItem("token")
        localStorage.removeItem("user_id")
        throw new Error("Session expirée")
    }

    return response.json()
}

export async function register(userData: any) {
    const response = await fetch(`${API_URL}/user`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
    })

    if (!response.ok) {
        const error = await response.json().catch(() => ({}))
        throw new Error(error.detail || "Échec de l'inscription")
    }

    return response.json()
}

export function logout() {
    localStorage.removeItem("token")
    localStorage.removeItem("user_id")
}
