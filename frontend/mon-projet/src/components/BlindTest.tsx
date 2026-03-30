import { useEffect, useState } from "react";
import type { Page } from "../types/Page";
import AddToPlaylistModal from "./AddToPlaylistModal";

interface BlindTestChoice {
  track_id: number;
  track_title?: string;
  artist_name?: string;
}

interface BlindTestQuestion {
  question_track_id: number;
  preview?: string;
  choices: BlindTestChoice[];
}

type BlindTestResult = {
  correct: boolean;
  correct_track_id: number;
  selected_track_id: number;
};

interface BlindTestProps {
  isConnected: boolean;
  userId: number | null;
  onNavigate: (page: Page) => void;
}

export default function BlindTest({ isConnected, userId, onNavigate }: BlindTestProps) {
  const [question, setQuestion] = useState<BlindTestQuestion | null>(null);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<BlindTestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  useEffect(() => {
    loadQuestion();
  }, []);

  const loadQuestion = async () => {
    setIsLoading(true);
    setError(null);
    setSelected(null);
    setResult(null);

    try {
      const response = await fetch("http://localhost:8000/blind-test/question", {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(localStorage.getItem("token") ? { Authorization: `Bearer ${localStorage.getItem("token")}` } : {}),
        },
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Erreur lors du chargement du blind-test");
      }

      const data = await response.json();
      setQuestion(data);
    } catch (err: any) {
      setError(err.message || "Impossible de charger une question");
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!question || selected === null) {
      setError("Veuillez sélectionner une réponse.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/blind-test/answer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(localStorage.getItem("token") ? { Authorization: `Bearer ${localStorage.getItem("token")}` } : {}),
        },
        body: JSON.stringify({
          question_track_id: question.question_track_id,
          selected_track_id: selected,
        }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Erreur lors de la validation");
      }

      const resultData: BlindTestResult = await response.json();
      setResult(resultData);
    } catch (err: any) {
      setError(err.message || "Une erreur est survenue");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleAddToPlaylist = () => {
    if (!question || !isConnected || !userId) {
      setError("Connectez-vous pour ajouter à une playlist.");
      return;
    }
    setModalOpen(true);
  };

  return (
    <div className="blind-test-container">
      <h2>Blind Test</h2>
      <p>Écoutez le court extrait et choisissez le bon titre.</p>
      <button onClick={() => onNavigate("accueil")} className="btn-secondary" style={{ marginBottom: "10px" }}>
        ← Retour
      </button>

      {isLoading ? (
        <p>Chargement question...</p>
      ) : error ? (
        <p className="error-text" style={{ color: "red" }}>{error}</p>
      ) : !question ? (
        <p>Aucune question disponible.</p>
      ) : (
        <>
          {question.preview ? (
            <audio controls src={question.preview} style={{ width: "100%", marginBottom: "15px" }} />
          ) : (
            <p>Aucun extrait disponible pour cette piste.</p>
          )}

          <div className="choices-grid" style={{ display: "grid", gap: "8px" }}>
            {question.choices.map((choice) => (
              <button
                key={choice.track_id}
                className={`choice-button ${selected === choice.track_id ? "selected" : ""}`}
                onClick={() => setSelected(choice.track_id)}
                style={{ padding: "10px", cursor: "pointer", textAlign: "left" }}
              >
                <strong>{choice.track_title}</strong>
                <br />
                <small>{choice.artist_name}</small>
              </button>
            ))}
          </div>

          <div style={{ marginTop: "15px" }}>
            <button onClick={submitAnswer} disabled={isSubmitting} className="btn-primary" style={{ marginRight: "10px" }}>
              Valider ma réponse
            </button>
            <button onClick={loadQuestion} className="btn-secondary">
              Nouvelle question
            </button>
          </div>

          {result && (
            <div style={{ marginTop: "20px" }}>
              <p>
                {result.correct ? "✅ Correct !" : "❌ Incorrect"} (Bonne réponse :
                {question.choices.find((c) => c.track_id === result.correct_track_id)?.track_title || "introuvable"})
              </p>

              {isConnected && userId && (
                <button className="btn-primary" onClick={handleAddToPlaylist}>
                  Ajouter cette piste à une playlist
                </button>
              )}

              <button className="btn-secondary" onClick={loadQuestion} style={{ marginLeft: "10px" }}>
                Question suivante
              </button>
            </div>
          )}

          {modalOpen && (
            <AddToPlaylistModal
              isOpen={modalOpen}
              onClose={() => setModalOpen(false)}
              trackId={question.question_track_id}
              userId={userId}
            />
          )}
        </>
      )}
    </div>
  );
}
