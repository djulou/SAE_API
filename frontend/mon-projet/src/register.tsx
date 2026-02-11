import { useState } from "react";
import type { Page } from "./types/Page"
import { register } from "./services/authService";
type Step = 1 | 2 | 3 | 4;

const musicTags = ["Rock", "Pop", "Rap", "Jazz", "Classique"];
const streamingServices = ["Netflix", "YouTube", "Twitch", "Disney+"];


type RegisterProps = {
    onNavigate: (page: Page) => void
}

export default function Register({ onNavigate }: RegisterProps) {
    const [step, setStep] = useState<Step>(1);
    const [name, setName] = useState("");
    const [loginIdentifier, setLoginIdentifier] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [selectedTags, setSelectedTags] = useState<string[]>([]);
    const [selectedServices, setSelectedServices] = useState<string[]>([]);

    const toggleTag = (tag: string) => {
        setSelectedTags((prev) =>
            prev.includes(tag) ? prev.filter((t) => t !== tag) : [...prev, tag]
        );
    };

    const toggleService = (service: string) => {
        setSelectedServices((prev) =>
            prev.includes(service)
                ? prev.filter((s) => s !== service)
                : [...prev, service]
        );
    };

    const nextStep = () => {
        if (step < 4) setStep((prev) => (prev + 1) as Step);
    };

    const prevStep = () => {
        if (step > 1) setStep((prev) => (prev - 1) as Step);
    };

    const handleSubmit = async () => {
        try {
            await register({
                email: email,
                user_login: loginIdentifier,
                user_mdp: password,
                pseudo: name
            });
            alert("Inscription terminée ! Connecte-toi maintenant.");
            onNavigate("login");
        } catch (err: any) {
            alert(err.message || "Erreur lors de l'inscription");
        }
    };

    return (
        <div className="login-page">
            <div className="login-container" style={{ maxWidth: step === 4 ? "500px" : "400px" }}>
                <h1 className="login-title">Inscription</h1>

                {/* Étape 1 */}
                {step === 1 && (
                    <div className="login-form">
                        <label>Pseudo (Nom affiché)</label>
                        <input
                            type="text"
                            placeholder="Ex: orchestra"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                        <label>Identifiant de connexion (Unique)</label>
                        <input
                            type="text"
                            placeholder="Ex: orchest_ra"
                            value={loginIdentifier}
                            onChange={(e) => setLoginIdentifier(e.target.value)}
                        />
                        <label>Email</label>
                        <input
                            type="email"
                            placeholder="Ton email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                        <label>Mot de passe</label>
                        <input
                            type="password"
                            placeholder="Ton mot de passe"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                )}

                {/* Étape 2 */}
                {step === 2 && (
                    <div className="login-form">
                        <label>Quels genres de musique aimes-tu ?</label>
                        <div className="tags-container" style={{ display: "flex", gap: "12px", flexWrap: "wrap" }}>
                            {musicTags.map((tag) => (
                                <button
                                    key={tag}
                                    className={`btn ${selectedTags.includes(tag) ? "confirm" : "cancel"}`}
                                    onClick={() => toggleTag(tag)}
                                    type="button"
                                >
                                    {tag}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Étape 3 */}
                {step === 3 && (
                    <div className="login-form">
                        <label>Quels services regardes-tu ?</label>
                        <div className="checkbox-group">
                            {streamingServices.map((service) => (
                                <label key={service} style={{ display: "block", fontSize: "20px", margin: "8px 0" }}>
                                    <input
                                        type="checkbox"
                                        checked={selectedServices.includes(service)}
                                        onChange={() => toggleService(service)}
                                        style={{ marginRight: "8px" }}
                                    />
                                    {service}
                                </label>
                            ))}
                        </div>
                    </div>
                )}

                {/* Étape 4 */}
                {step === 4 && (
                    <div className="login-form">
                        <label>Vérifie tes choix :</label>
                        <p><strong>Nom affiché :</strong> {name}</p>
                        <p><strong>Identifiant :</strong> {loginIdentifier}</p>
                        <p><strong>Email :</strong> {email}</p>
                        <p><strong>Genres :</strong> {selectedTags.join(", ")}</p>
                        <p><strong>Services :</strong> {selectedServices.join(", ")}</p>
                    </div>
                )}

                {/* Boutons */}
                <div className="login-actions">
                    {step > 1 && (
                        <button className="btn cancel" type="button" onClick={prevStep}>
                            Précédent
                        </button>
                    )}
                    {step < 4 && (
                        <button className="btn confirm" type="button" onClick={nextStep}>
                            Suivant
                        </button>
                    )}
                    {step === 4 && (
                        <button
                            className="btn confirm"
                            type="button"
                            onClick={() => {
                                handleSubmit();
                                onNavigate("detail_compte");
                            }}
                        >
                            Confirmer
                        </button>

                    )}
                </div>
            </div>
        </div>
    );
}
