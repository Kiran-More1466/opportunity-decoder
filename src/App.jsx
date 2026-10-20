import { useEffect, useState } from 'react'
import Header from './components/Header.jsx'
import LandingPage from './pages/LandingPage.jsx'
import OpportunityInputPage from './pages/OpportunityInputPage.jsx'

function App() {
  const [path, setPath] = useState(window.location.pathname)

  useEffect(() => {
    const handlePopState = () => setPath(window.location.pathname)
    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  function navigate(nextPath) {
    window.history.pushState({}, '', nextPath)
    setPath(nextPath)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const isInputPage = path === '/analyze'

  return (
    <>
      <Header onNavigate={navigate} />
      {isInputPage ? (
        <OpportunityInputPage onNavigate={navigate} />
      ) : (
        <LandingPage onNavigate={navigate} />
      )}
    </>
  )
}

export default App
