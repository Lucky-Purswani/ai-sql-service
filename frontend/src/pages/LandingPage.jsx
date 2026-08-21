import { Link } from 'react-router-dom'
import Navbar from '../components/common/Navbar'
import './LandingPage.css'

export default function LandingPage() {
  return (
    <div className="landing">
      {/* Decorative grid background */}
      <div className="landing__grid" aria-hidden="true" />

      {/* Floating particles */}
      <div className="landing__particles" aria-hidden="true">
        <span className="particle particle--1" />
        <span className="particle particle--2" />
        <span className="particle particle--3" />
        <span className="particle particle--4" />
        <span className="particle particle--5" />
      </div>

      <Navbar
        rightSlot={
          <Link to="/login" className="landing__btn landing__btn--primary">
            Get Started
          </Link>
        }
      />

      {/* Hero */}
      <main className="landing__hero">
        <div className="landing__badge">
          <span className="landing__badge-dot" />
          Natural Language to SQL
        </div>

        <h1 className="landing__title">
          Talk to your
          <br />
          <span className="landing__title-accent">database.</span>
        </h1>

        <p className="landing__subtitle">
          Connect any PostgreSQL database and ask questions in plain English.
          <br />
          Our AI translates your words into safe, read-only SQL — instantly.
        </p>

        <div className="landing__cta">
          <Link to="/signup" className="landing__btn landing__btn--primary landing__btn--lg">
            Start Free
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </Link>
          <Link to="/login" className="landing__btn landing__btn--outline landing__btn--lg">
            Log in
          </Link>
        </div>
      </main>

      {/* Footer line */}
      <footer className="landing__footer">
        <span>Built with FastAPI + React</span>
        <span className="landing__footer-sep">·</span>
        <span>Read-only queries only</span>
        <span className="landing__footer-sep">·</span>
        <span>Your data never leaves your server</span>
      </footer>
    </div>
  )
}
