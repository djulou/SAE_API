import { useState, useEffect, useRef } from "react"
import type { Page } from "../types/Page"
import AddToPlaylistModal from "./AddToPlaylistModal"

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

type Difficulty = "facile" | "moyen" | "difficile";

interface BlindTestConfig {
  numQuestions: number;
  difficulty: Difficulty;
}

export default function BlindTest({ isConnected, userId, onNavigate }: BlindTestProps) {
  const [config, setConfig] = useState<BlindTestConfig>({ numQuestions: 5, difficulty: "moyen" });
  const [configSubmitted, setConfigSubmitted] = useState(false);
  const [questions, setQuestions] = useState<BlindTestQuestion[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [result, setResult] = useState<BlindTestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [showList, setShowList] = useState(false);
  const audioRef = useRef<HTMLAudioElement>(null);

  const difficultyDurations: Record<Difficulty, number> = {
    facile: 10,
    moyen: 5,
    difficile: 3,
  };

  useEffect(() => {
    if (audioRef.current && config) {
      const duration = difficultyDurations[config.difficulty];
      audioRef.current.addEventListener('loadedmetadata', () => {
        if (audioRef.current!.duration > duration) {
          audioRef.current!.currentTime = 0;
        }
      });
      audioRef.current.addEventListener('timeupdate', () => {
        if (audioRef.current!.currentTime >= duration) {
          audioRef.current!.pause();
          audioRef.current!.currentTime = 0;
        }
      });
    }
  }, [config]);

  const loadQuestions = async () => {
    if (!config) return;
    setIsLoading(true);
    setError(null);
    setSelected(null);
    setResult(null);
    setCurrentQuestionIndex(0);

    try {
      const questionsPromises = Array.from({ length: config.numQuestions }, () =>
        fetch("http://127.0.0.1:8000/blind-test/question", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            ...(localStorage.getItem("token") ? { Authorization: `Bearer ${localStorage.getItem("token")}` } : {}),
          },
        }).then(res => res.json())
      );

      const loadedQuestions = await Promise.all(questionsPromises);
      setQuestions(loadedQuestions);
    } catch (err: any) {
      setError(err.message || "Impossible de charger les questions");
    } finally {
      setIsLoading(false);
    }
  };

  const submitAnswer = async () => {
    if (!questions[currentQuestionIndex] || selected === null) {
      setError("Veuillez sélectionner une réponse.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/blind-test/answer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(localStorage.getItem("token") ? { Authorization: `Bearer ${localStorage.getItem("token")}` } : {}),
        },
        body: JSON.stringify({
          question_track_id: questions[currentQuestionIndex].question_track_id,
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

  const nextQuestion = () => {
    setSelected(null);
    setResult(null);
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      // Fin du blind test
      setCurrentQuestionIndex(questions.length);
    }
  };

  const handleAddToPlaylist = () => {
    if (!questions[currentQuestionIndex] || !isConnected || !userId) {
      setError("Connectez-vous pour ajouter à une playlist.");
      return;
    }
    setModalOpen(true);
  };

  const handleConfigSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setConfigSubmitted(true);
    loadQuestions();
  };

  if (!configSubmitted) {
    return (
      <div className="blind-test-container">
        <div className="blind-test-card">
          <div className="blind-test-header">
            <div>
              <h2>Configuration du Blind Test</h2>
              <p>Configurez votre session de blind test.</p>
            </div>
            <button onClick={() => onNavigate("accueil")} className="btn-secondary">
              ← Retour
            </button>
          </div>

          <form onSubmit={handleConfigSubmit} className="blind-test-config">
            <div className="config-field">
              <label htmlFor="numQuestions">Nombre de musiques :</label>
              <input
                type="number"
                id="numQuestions"
                min="1"
                max="20"
                value={config?.numQuestions || 5}
                onChange={(e) => setConfig(prev => ({ ...prev!, numQuestions: parseInt(e.target.value) }))}
                required
              />
            </div>

            <div className="config-field">
              <label htmlFor="difficulty">Niveau de difficulté :</label>
              <select
                id="difficulty"
                value={config?.difficulty || "moyen"}
                onChange={(e) => setConfig(prev => ({ ...prev!, difficulty: e.target.value as Difficulty }))}
                required
              >
                <option value="facile">Facile (10 secondes)</option>
                <option value="moyen">Moyen (5 secondes)</option>
                <option value="difficile">Difficile (3 secondes)</option>
              </select>
            </div>

            <button type="submit" className="btn-primary">Commencer le Blind Test</button>
          </form>
        </div>
      </div>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="blind-test-container">
      <div className="blind-test-card">
        <div className="blind-test-header">
          <div>
            <h2>Blind Test</h2>
            <p>Question {currentQuestionIndex + 1} / {questions.length} - Difficulté : {config.difficulty}</p>
          </div>
          <div className="header-actions">
            <button onClick={() => setShowList(!showList)} className="btn-secondary">
              {showList ? "Masquer la liste" : "Voir la liste"}
            </button>
            <button onClick={() => onNavigate("accueil")} className="btn-secondary">
              ← Retour
            </button>
          </div>
        </div>

        {showList && (
          <div className="blind-test-list">
            <h3>Liste des musiques du Blind Test</h3>
            <ul>
              {questions.map((q, index) => (
                <li key={index}>
                  {index + 1}. {q.choices.find(c => c.track_id === q.question_track_id)?.track_title} - {q.choices.find(c => c.track_id === q.question_track_id)?.artist_name}
                </li>
              ))}
            </ul>
          </div>
        )}

        {isLoading ? (
          <p className="blind-test-status">Chargement des questions...</p>
        ) : error ? (
          <p className="error-text">{error}</p>
        ) : currentQuestionIndex >= questions.length ? (
          <p className="blind-test-status">Blind Test terminé !</p>
        ) : !currentQuestion ? (
          <p className="blind-test-status">Aucune question disponible.</p>
        ) : (
          <>
            <div className="blind-test-audio">
              {currentQuestion.preview ? (
                <audio ref={audioRef} controls src={currentQuestion.preview} className="audio-player" />
              ) : (
                <p className="blind-test-status">Aucun extrait disponible pour cette piste.</p>
              )}
            </div>

            <div className="choices-grid">
              {currentQuestion.choices.map((choice) => (
                <button
                  key={choice.track_id}
                  className={`choice-button ${selected === choice.track_id ? "selected" : ""}`}
                  onClick={() => setSelected(choice.track_id)}
                >
                  <strong>{choice.track_title}</strong>
                  <small>{choice.artist_name}</small>
                </button>
              ))}
            </div>

            <div className="blind-test-actions">
              <button
                onClick={submitAnswer}
                disabled={isSubmitting || result !== null}
                className="btn-primary"
              >
                Valider ma réponse
              </button>
              {result && (
                <button onClick={nextQuestion} className="btn-secondary">
                  {currentQuestionIndex < questions.length - 1 ? "Question suivante" : "Terminer"}
                </button>
              )}
            </div>

            {result && (
              <div className="blind-test-result">
                <p className="result-message">
                  {result.correct ? "✅ Correct !" : "❌ Incorrect"}
                </p>
                <p className="result-subtitle">
                  Bonne réponse : <strong>{currentQuestion.choices.find((c) => c.track_id === result.correct_track_id)?.track_title || "introuvable"}</strong>
                </p>

                <div className="blind-test-actions">
                  {isConnected && userId && (
                    <button className="btn-primary" onClick={handleAddToPlaylist}>
                      Ajouter cette piste à une playlist
                    </button>
                  )}
                </div>
              </div>
            )}

            {modalOpen && (
              <AddToPlaylistModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                trackId={currentQuestion.question_track_id}
                userId={userId}
              />
            )}
          </>
        )}
      </div>
    </div>
  )
}
