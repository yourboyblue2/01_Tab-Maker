import { useState } from 'react'
import UrlInput from './components/UrlInput'
import ProgressSteps from './components/ProgressSteps'
import TabDisplay from './components/TabDisplay'
import './App.css'

const STEPS = ['Download', 'Isolate Guitar', 'Transcribe', 'Generate Tab']

export default function App() {
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const [activeStep, setActiveStep] = useState(-1)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  async function handleGenerate(url) {
    setStatus('loading')
    setError(null)
    setResult(null)
    setActiveStep(0)

    // Advance steps visually while backend runs (~8s per step)
    const stepTimer = setInterval(() => {
      setActiveStep(prev => (prev < STEPS.length - 1 ? prev + 1 : prev))
    }, 8000)

    try {
      const res = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      })
      clearInterval(stepTimer)

      if (!res.ok) {
        const data = await res.json()
        throw new Error(data.detail || 'Something went wrong')
      }

      const data = await res.json()
      setActiveStep(STEPS.length - 1)
      setResult(data)
      setStatus('done')
    } catch (err) {
      clearInterval(stepTimer)
      setError(err.message)
      setStatus('error')
      setActiveStep(-1)
    }
  }

  function handleReset() {
    setStatus('idle')
    setActiveStep(-1)
    setResult(null)
    setError(null)
  }

  return (
    <div className="app">
      <header>
        <h1>TabMaker</h1>
        <p className="subtitle">Paste a YouTube URL. Get guitar tabs.</p>
      </header>

      <main>
        {(status === 'idle' || status === 'error') && (
          <UrlInput onGenerate={handleGenerate} />
        )}

        {status === 'error' && (
          <div className="error-box">
            <p>{error}</p>
            <button className="btn-secondary" onClick={handleReset}>Try again</button>
          </div>
        )}

        {status === 'loading' && (
          <ProgressSteps steps={STEPS} activeStep={activeStep} />
        )}

        {status === 'done' && result && (
          <>
            <TabDisplay title={result.title} bpm={result.bpm} tabText={result.tab_text} midiB64={result.midi_b64} />
            <button className="btn-secondary reset-btn" onClick={handleReset}>Generate another</button>
          </>
        )}
      </main>
    </div>
  )
}
