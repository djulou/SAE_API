import { useState, useEffect } from "react";
import InfoUser from "./components/info_user";
import StatsUser from "./components/stats_user";
import "./details_compte.css";

interface UserData {
    user_id: number;
    email: string;
    pseudo?: string;
    user_login: string;
}

export default function DetailCompte() {
    const [user, setUser] = useState<UserData | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchUserData = async () => {
            const token = localStorage.getItem("token");
            if (!token) {
                setError("Session expirée. Veuillez vous reconnecter.");
                return;
            }
            try {
                const response = await fetch("http://127.0.0.1:8000/user", {
                    method: "GET",
                    headers: {
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    }
                });
                if (!response.ok) throw new Error("Erreur de récupération.");
                const data = await response.json();
                setUser(data);
            } catch (err: any) {
                setError(err.message);
            }
        };
        fetchUserData();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("token");
        window.location.href = "/login";
    };

    if (error) return (
        <div className="page-wrapper center">
            <div className="alert error">⚠️ {error}</div>
        </div>
    );

    if (!user) return <div className="page-wrapper center"><div className="loader"></div></div>;

    return (
        <div className="page-wrapper">
            <div className="dashboard-container">
                {/* COLONNE GAUCHE : Profil permanent */}
                <aside className="sidebar">
                    <div className="profile-summary">
                        <div className="avatar-large">
                            {(user.pseudo || user.user_login || "U").charAt(0).toUpperCase()}
                        </div>
                        <h2>{user.pseudo || user.user_login}</h2>
                    </div>

                    <div className="sidebar-content">
                        <InfoUser email={user.email} id={user.user_id.toString()} />
                    </div>

                    <div className="sidebar-footer">
                        {/* Utilisation de btn-logout pour correspondre à ton CSS de charte */}
                        <button className="btn-logout" onClick={handleLogout}>Déconnexion</button>
                        <button className="btn-ghost" onClick={() => {/* Logique suppression */}}>
                            Supprimer le compte
                        </button>
                    </div>
                </aside>

                <main className="content-area">
                    <header className="content-header">
                        <h1>Tableau de bord</h1>
                        <p>Aperçu de votre activité et de vos préférences musicales.</p>
                    </header>
                    
                    <div className="stats-wrapper">
                        <StatsUser  />
                    </div>
                </main>
            </div>
        </div>
    );
}