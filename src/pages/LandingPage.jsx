import SectionLabel from '../components/SectionLabel.jsx'

const features = [
  {
    number: '01',
    title: 'See the whole picture',
    description: 'Bring the details together and understand what an opportunity is really asking of you.',
  },
  {
    number: '02',
    title: 'Find the important parts',
    description: 'Focus on the signals, trade-offs, and open questions that deserve your attention.',
  },
  {
    number: '03',
    title: 'Choose your next step',
    description: 'Get to a clearer point of view so you can decide how to move forward.',
  },
]

const steps = [
  ['01', 'Share the opportunity', 'Start with the information you already have.'],
  ['02', 'Get a clearer view', 'Organize the details into the questions that matter.'],
  ['03', 'Decide what comes next', 'Use your perspective to make a thoughtful next move.'],
]

function LandingPage({ onNavigate }) {
  return (
    <main>
      <section className="hero page-wrap">
        <div className="hero-copy">
          <SectionLabel>Clarity for what’s next</SectionLabel>
          <h1>Good opportunities deserve a <span>closer look.</span></h1>
          <p className="hero-description">
            Make sense of the details, spot what matters, and move forward with a little more clarity.
          </p>
          <button className="primary-button" type="button" onClick={() => onNavigate('/analyze')}>
            Analyze Now <span aria-hidden="true">↗</span>
          </button>
          <p className="hero-note">A thoughtful starting point for your next decision.</p>
        </div>
        <div className="hero-art" aria-label="A simple illustration of a decision taking shape" role="img">
          <div className="art-topline"><span>YOUR NEXT MOVE</span><span className="art-dot" /></div>
          <div className="art-question">What’s the<br /><em>real opportunity?</em></div>
          <div className="art-lines" aria-hidden="true">
            <span className="art-line line-long" /><span className="art-line line-medium" />
          </div>
          <div className="art-bottom"><span>Look closer</span><span className="art-arrow" aria-hidden="true">↘</span></div>
          <div className="art-index" aria-hidden="true">01 / 03</div>
        </div>
      </section>

      <section className="features-section" aria-labelledby="features-title">
        <div className="page-wrap">
          <div className="section-heading">
            <div><SectionLabel>A clearer perspective</SectionLabel><h2 id="features-title">Make the details<br />work for <span>you.</span></h2></div>
            <p>Big decisions can feel easier when you know what to look for. Start with a clearer view of the opportunity in front of you.</p>
          </div>
          <div className="feature-list">
            {features.map((feature) => (
              <article className="feature-item" key={feature.number}>
                <span className="feature-number">{feature.number}</span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
                <span className="feature-arrow" aria-hidden="true">↗</span>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="how-section page-wrap" id="how-it-works" aria-labelledby="how-title">
        <div className="how-intro">
          <SectionLabel>Simple by design</SectionLabel>
          <h2 id="how-title">A little more clarity,<br />in <span>three steps.</span></h2>
        </div>
        <div className="steps-list">
          {steps.map(([number, title, description]) => (
            <article className="step-item" key={number}>
              <span className="step-number">{number}</span>
              <div><h3>{title}</h3><p>{description}</p></div>
              <span className="step-mark" aria-hidden="true">+</span>
            </article>
          ))}
          <button className="text-link" type="button" onClick={() => onNavigate('/analyze')}>Take a closer look <span aria-hidden="true">↗</span></button>
        </div>
      </section>

      <footer className="site-footer page-wrap"><a className="brand" href="/" onClick={(event) => { event.preventDefault(); onNavigate('/') }}><span className="brand-mark" aria-hidden="true">O</span><span>Opportunity Decoder</span></a><span>Make your next move a thoughtful one.</span></footer>
    </main>
  )
}

export default LandingPage
