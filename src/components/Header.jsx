function Header({ onNavigate }) {
  return (
    <header className="site-header">
      <a
        className="brand"
        href="/"
        onClick={(event) => {
          event.preventDefault()
          onNavigate('/')
        }}
        aria-label="Opportunity Decoder home"
      >
        <span className="brand-mark" aria-hidden="true">O</span>
        <span>Opportunity Decoder</span>
      </a>
      <nav className="header-nav" aria-label="Main navigation">
        <a href="/#how-it-works" onClick={(event) => {
          if (window.location.pathname === '/') {
            event.preventDefault()
            document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
          }
        }}>How it works</a>
        <button className="nav-cta" type="button" onClick={() => onNavigate('/analyze')}>
          Analyze an opportunity <span aria-hidden="true">↗</span>
        </button>
      </nav>
    </header>
  )
}

export default Header
