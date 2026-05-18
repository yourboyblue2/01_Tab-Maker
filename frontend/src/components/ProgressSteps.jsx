import './ProgressSteps.css'

export default function ProgressSteps({ steps, activeStep }) {
  return (
    <div className="progress-steps">
      <p className="progress-label">Processing your song...</p>
      <div className="steps">
        {steps.map((step, i) => {
          const isDone = i < activeStep
          const isActive = i === activeStep
          return (
            <div key={step} className={`step ${isDone ? 'done' : ''} ${isActive ? 'active' : ''}`}>
              <div className="step-icon">
                {isDone ? '✓' : isActive ? <span className="spinner" /> : i + 1}
              </div>
              <span className="step-label">{step}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
