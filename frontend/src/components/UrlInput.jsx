import { useState } from 'react'
import './UrlInput.css'

export default function UrlInput({ onGenerate }) {
  const [url, setUrl] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = url.trim()
    if (!trimmed) return
    onGenerate(trimmed)
  }

  return (
    <form className="url-input" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="https://www.youtube.com/watch?v=..."
        value={url}
        onChange={e => setUrl(e.target.value)}
        autoFocus
      />
      <button type="submit" className="btn-primary" disabled={!url.trim()}>
        Generate Tab
      </button>
    </form>
  )
}
