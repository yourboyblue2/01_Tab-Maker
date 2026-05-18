import { useState } from 'react'
import './TabDisplay.css'

export default function TabDisplay({ title, bpm, tabText, midiB64 }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    navigator.clipboard.writeText(tabText).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  function handleDownloadTab() {
    const blob = new Blob([`Song: ${title}\nBPM: ${bpm}\n\n${tabText}`], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/[^a-z0-9]/gi, '_')}_tab.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  function handleDownloadMidi() {
    const bytes = Uint8Array.from(atob(midiB64), c => c.charCodeAt(0))
    const blob = new Blob([bytes], { type: 'audio/midi' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${title.replace(/[^a-z0-9]/gi, '_')}.mid`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="tab-display">
      <div className="tab-header">
        <div className="tab-meta">
          <h2>{title}</h2>
          <span className="bpm">{bpm} BPM</span>
        </div>
        <div className="tab-actions">
          <button className="btn-secondary" onClick={handleCopy}>
            {copied ? 'Copied!' : 'Copy'}
          </button>
          <button className="btn-secondary" onClick={handleDownloadTab}>
            Download .txt
          </button>
          {midiB64 && (
            <button className="btn-secondary" onClick={handleDownloadMidi}>
              Download MIDI
            </button>
          )}
        </div>
      </div>
      <pre className="tab-content">{tabText}</pre>
    </div>
  )
}
