'use client';

/*
  QuizRunner
  ----------
  Preview quiz-taking flow: sample multiple-choice questions, answer
  selection kept in local React state, and a results screen computed
  client-side on submit. No backend, no persistence — see
  /portal/CONVENTIONS.md.
*/

import { useState } from 'react';
import { Badge } from './ui';

export default function QuizRunner({ questions }) {
  const [started, setStarted] = useState(false);
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);

  const allAnswered = questions.every((q) => answers[q.id] !== undefined);
  const score = questions.reduce((sum, q) => (answers[q.id] === q.correctIndex ? sum + 1 : sum), 0);

  function selectAnswer(questionId, optionIndex) {
    if (submitted) return;
    setAnswers((prev) => ({ ...prev, [questionId]: optionIndex }));
  }

  function reset() {
    setAnswers({});
    setSubmitted(false);
    setStarted(false);
  }

  if (!started) {
    return (
      <div className="intro">
        <p>
          This is a short sample of {questions.length} question{questions.length === 1 ? '' : 's'} for preview
          purposes — the full quiz will be available once the portal is connected to real course content.
        </p>
        <button type="button" className="primary-btn" onClick={() => setStarted(true)}>
          Start sample quiz
        </button>
        <style jsx>{`
          .intro { display: flex; flex-direction: column; gap: 16px; align-items: flex-start; }
          .intro p { color: var(--ink-muted); font-size: 13.5px; line-height: 1.6; margin: 0; }
          .primary-btn { background: var(--navy); color: #fff; border: none; border-radius: var(--radius-sm); padding: 10px 20px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
          .primary-btn:hover { background: var(--navy-dark); }
        `}</style>
      </div>
    );
  }

  if (submitted) {
    const pct = Math.round((score / questions.length) * 100);
    return (
      <div className="results">
        <div className="score-banner">
          <span className="score-value">{score} / {questions.length}</span>
          <span className="score-pct">{pct}% correct</span>
        </div>

        <ol className="review">
          {questions.map((q, i) => {
            const chosen = answers[q.id];
            const correct = chosen === q.correctIndex;
            return (
              <li key={q.id}>
                <div className="review-head">
                  <span className="qnum">Question {i + 1}</span>
                  <Badge tone={correct ? 'success' : 'alert'}>{correct ? 'Correct' : 'Incorrect'}</Badge>
                </div>
                <p className="prompt">{q.prompt}</p>
                <p className="answer-line">
                  Your answer: <strong>{q.options[chosen]}</strong>
                </p>
                {!correct && (
                  <p className="answer-line correct-line">
                    Correct answer: <strong>{q.options[q.correctIndex]}</strong>
                  </p>
                )}
              </li>
            );
          })}
        </ol>

        <button type="button" className="secondary-btn" onClick={reset}>
          Retake sample quiz
        </button>

        <style jsx>{`
          .results { display: flex; flex-direction: column; gap: 20px; }
          .score-banner { display: flex; align-items: baseline; gap: 12px; background: var(--manuscript); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 18px 22px; }
          .score-value { font-family: 'Fraunces', serif; font-size: 26px; color: var(--navy); }
          .score-pct { font-size: 13.5px; color: var(--ink-muted); }
          .review { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 14px; }
          .review li { border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px 18px; }
          .review-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
          .qnum { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); }
          .prompt { font-size: 14px; color: var(--ink); margin: 0 0 8px; }
          .answer-line { font-size: 13px; color: var(--ink-muted); margin: 0; }
          .correct-line { color: var(--emerald); }
          .secondary-btn { align-self: flex-start; background: var(--surface); color: var(--navy); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 10px 20px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
          .secondary-btn:hover { background: var(--manuscript); }
        `}</style>
      </div>
    );
  }

  return (
    <form
      className="quiz-form"
      onSubmit={(e) => {
        e.preventDefault();
        setSubmitted(true);
      }}
    >
      <ol className="questions">
        {questions.map((q, i) => (
          <li key={q.id}>
            <fieldset>
              <legend>
                <span className="qnum">Question {i + 1}</span>
                {q.prompt}
              </legend>
              <div className="options">
                {q.options.map((opt, idx) => (
                  <label key={idx} className="option">
                    <input
                      type="radio"
                      name={q.id}
                      value={idx}
                      checked={answers[q.id] === idx}
                      onChange={() => selectAnswer(q.id, idx)}
                    />
                    <span>{opt}</span>
                  </label>
                ))}
              </div>
            </fieldset>
          </li>
        ))}
      </ol>

      <button type="submit" className="primary-btn" disabled={!allAnswered}>
        Submit answers
      </button>
      {!allAnswered && <p className="hint">Answer every question to submit.</p>}

      <style jsx>{`
        .quiz-form { display: flex; flex-direction: column; gap: 20px; align-items: flex-start; }
        .questions { list-style: none; margin: 0; padding: 0; width: 100%; display: flex; flex-direction: column; gap: 16px; }
        fieldset { border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px 18px; margin: 0; }
        legend { display: flex; flex-direction: column; gap: 4px; font-size: 14px; color: var(--ink); padding: 0 4px; }
        .qnum { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.03em; color: var(--ink-muted); }
        .options { display: flex; flex-direction: column; gap: 8px; margin-top: 10px; }
        .option { display: flex; align-items: center; gap: 10px; font-size: 13.5px; color: var(--ink); cursor: pointer; }
        .option input { accent-color: var(--navy); width: 16px; height: 16px; flex-shrink: 0; }
        .primary-btn { background: var(--navy); color: #fff; border: none; border-radius: var(--radius-sm); padding: 10px 20px; font-size: 13.5px; font-weight: 600; cursor: pointer; }
        .primary-btn:hover:not(:disabled) { background: var(--navy-dark); }
        .primary-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .hint { font-size: 12.5px; color: var(--ink-muted); margin: -12px 0 0; }
      `}</style>
    </form>
  );
}
