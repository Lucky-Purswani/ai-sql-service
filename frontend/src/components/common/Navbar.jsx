import { Link } from 'react-router-dom'
import '../../styles/auth.css'

/**
 * Shared navbar used across Landing, Login, Signup, and VerifyOtp pages.
 * Keeps the [AI SQL] logo placement and border-bottom consistent everywhere.
 */
export default function Navbar({ rightSlot }) {
  return (
    <nav className="shared-nav">
      <Link to="/" className="shared-nav__logo">
        <span className="shared-nav__bracket">[</span>
        <span className="shared-nav__text">AI SQL</span>
        <span className="shared-nav__bracket">]</span>
      </Link>

      {rightSlot && (
        <div className="shared-nav__right">{rightSlot}</div>
      )}
    </nav>
  )
}
