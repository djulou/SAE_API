import { useState } from "react";
import type {Page} from "./types/Page"
type Step = 1 | 2 | 3 | 4;

const musicTags = ["Rock", "Pop", "Rap", "Jazz", "Classique"];
const streamingServices = ["Netflix", "YouTube", "Twitch", "Disney+"];


type RegisterProps = {
  onNavigate: (page: Page) => void
}

export default function Register({onNavigate}:RegisterProps) {
    const [step, setStep] = useState<Step>(1);
    const [name, setName] = useState("");
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

    const handleSubmit = () => {
        console.log({ name, email, password, selectedTags, selectedServices });
        alert("Inscription terminée !");
    };

    return (
        <div className="login-page">
            <div className="login-container">
                <h1 className="login-title">Inscription</h1>

                {/* Étape 1 */}
                {step === 1 && (
                    <div className="login-form">
                        <label>Nom complet</label>
                        <input
                            type="text"
                            placeholder="Ton nom"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
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
                        <p><strong>Nom :</strong> {name}</p>
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
