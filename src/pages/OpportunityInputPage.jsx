import { useState } from 'react'

const API_BASE_URL = (import.meta.env.VITE_API_URL || '').trim().replace(/\/+$/, '')

const initialForm = {
  description: '', companyName: '', sourceUrl: '', education: '', skills: '',
  graduationYear: '', projectsExperience: '', dailyPreparationMinutes: '',
}

function EligibilityList({ title, requirements }) {
  return (
    <section className="report-section">
      <h3>{title}</h3>
      {requirements.length ? <ul className="report-list">{requirements.map((item, index) => (
        <li className="requirement-item" key={`${item.requirement}-${index}`}>
          <div className="requirement-heading"><strong>{item.requirement}</strong><span className={`status-pill status-${item.status.toLowerCase().replace(' ', '-')}`}>{item.status}</span></div>
          <p>{item.evidence}</p>
        </li>
      ))}</ul> : <p className="report-empty">No requirements in this category were identified in the provided description.</p>}
    </section>
  )
}

function AnalysisReport({ report }) {
  return (
    <section className="analysis-report" aria-live="polite" aria-labelledby="report-title">
      <div className="report-header"><p className="section-label"><span aria-hidden="true" />Your opportunity report</p><h2 id="report-title">A clearer view of the role.</h2></div>
      <section className="report-section"><h3>Role summary</h3><p>{report.role_summary}</p></section>
      <div className="report-columns"><EligibilityList title="Mandatory requirements" requirements={report.mandatory_requirements} /><EligibilityList title="Preferred requirements" requirements={report.preferred_requirements} /></div>
      <div className="report-columns">
        <section className="report-section"><h3>Demonstrated skills</h3>{report.demonstrated_skills.length ? <ul className="report-list">{report.demonstrated_skills.map((skill, index) => <li key={`${skill.skill}-${index}`}><strong>{skill.skill}</strong><p>{skill.evidence}</p></li>)}</ul> : <p className="report-empty">No skills could be confirmed from the information provided.</p>}</section>
        <section className="report-section"><h3>Potential skill gaps</h3>{report.potential_skill_gaps.length ? <ul className="report-list">{report.potential_skill_gaps.map((gap, index) => <li key={`${gap.skill}-${index}`}><strong>{gap.skill}</strong><p>{gap.reason}</p></li>)}</ul> : <p className="report-empty">No specific gaps were identified from the available information.</p>}</section>
      </div>
      <section className="report-section"><h3>Preparation actions</h3>{report.preparation_actions.length ? <ol className="action-list">{report.preparation_actions.map((action, index) => <li key={`${action.action}-${index}`}><span className="action-priority">{index + 1}</span><div><strong>{action.action}</strong><p>{action.reason}</p></div></li>)}</ol> : <p className="report-empty">No preparation actions were returned.</p>}</section>
      <section className="report-section"><h3>Details to clarify</h3>{report.missing_or_ambiguous_details.length ? <ul className="report-list">{report.missing_or_ambiguous_details.map((detail, index) => <li key={`${detail}-${index}`}>{detail}</li>)}</ul> : <p className="report-empty">No important missing details were identified.</p>}</section>
      <p className="report-disclaimer">This report organizes the information you provided. It does not predict hiring outcomes or guarantee selection.</p>
    </section>
  )
}

function OpportunityInputPage({ onNavigate }) {
  const [form, setForm] = useState(initialForm)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function updateField(event) {
    const { name, value } = event.target
    setForm((current) => ({ ...current, [name]: value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setReport(null)
    setIsSubmitting(true)
    const payload = {
      opportunity_description: form.description.trim(),
      company_name: form.companyName.trim() || null,
      source_url: form.sourceUrl.trim() || null,
      student_education: form.education.trim(),
      student_skills: form.skills.split(/[\n,]/).map((skill) => skill.trim()).filter(Boolean),
      graduation_year: form.graduationYear ? Number(form.graduationYear) : null,
      projects_or_experience: form.projectsExperience.trim() || null,
      daily_preparation_minutes: form.dailyPreparationMinutes ? Number(form.dailyPreparationMinutes) : null,
    }

    const controller = new AbortController()
    const requestTimeout = window.setTimeout(() => controller.abort(), 70_000)
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal: controller.signal })
      const result = await response.json().catch(() => null)
      if (!response.ok) {
        const detail = typeof result?.detail === 'string' ? result.detail : ''
        if (response.status >= 500 && !detail) {
          throw new Error('The analysis service could not be reached. Check that the FastAPI backend is running, then retry.')
        }
        throw new Error(detail || 'The analysis could not be completed. Please try again.')
      }
      if (!result) throw new Error('The analysis service returned an unreadable response. Please retry.')
      setReport(result)
    } catch (requestError) {
      setError(requestError.name === 'AbortError'
        ? 'The analysis is taking longer than expected. Your entries are saved here—please retry.'
        : requestError instanceof TypeError
          ? 'Could not reach the analysis service. Check that the FastAPI backend is running, then retry.'
        : requestError.message || 'Could not reach the analysis service. Check that the backend is running and try again.')
    } finally {
      window.clearTimeout(requestTimeout)
      setIsSubmitting(false)
    }
  }

  return (
    <main className="input-page page-wrap">
      <button className="back-link" type="button" onClick={() => onNavigate('/')}><span aria-hidden="true">←</span> Back to home</button>
      <div className="input-layout">
        <div className="input-intro">
          <p className="section-label"><span aria-hidden="true" />Your opportunity</p>
          <h1>Let’s take a<br /><span>closer look.</span></h1>
          <p>Share the role and a little about your background. We’ll organize what’s known and flag what still needs a closer look.</p>
        </div>
        <form className="opportunity-form" onSubmit={handleSubmit}>
          <div className="form-heading"><span>01 — GET STARTED</span><p>Tell us what’s on your mind.</p></div>
          <label htmlFor="opportunity-description">Job or internship description <span className="required-mark">Required</span></label>
          <textarea id="opportunity-description" name="description" rows="7" required minLength="20" maxLength="20000" value={form.description} onChange={updateField} placeholder="Paste the full role description, including responsibilities and requirements." />
          <div className="form-grid">
            <div><label htmlFor="company-name">Company name <span>Optional</span></label><input id="company-name" name="companyName" type="text" maxLength="200" value={form.companyName} onChange={updateField} placeholder="Company or organization" /></div>
            <div><label htmlFor="source-url">Source URL <span>Optional</span></label><input id="source-url" name="sourceUrl" type="url" value={form.sourceUrl} onChange={updateField} placeholder="https://…" /></div>
          </div>
          <label htmlFor="student-education">Your education</label>
          <textarea id="student-education" name="education" rows="3" required maxLength="4000" value={form.education} onChange={updateField} placeholder="Degree or program, institution, and relevant focus areas." />
          <label htmlFor="student-skills">Your skills <span className="field-hint">Separate with commas or new lines</span></label>
          <textarea id="student-skills" name="skills" rows="3" required value={form.skills} onChange={updateField} placeholder="For example: research, Python, communication…" />
          <div className="form-grid">
            <div><label htmlFor="graduation-year">Graduation year <span>Optional</span></label><input id="graduation-year" name="graduationYear" type="number" min="1900" max="2200" value={form.graduationYear} onChange={updateField} placeholder="e.g. 2027" /></div>
            <div><label htmlFor="daily-preparation">Daily prep time <span>Optional</span></label><input id="daily-preparation" name="dailyPreparationMinutes" type="number" min="1" max="1440" value={form.dailyPreparationMinutes} onChange={updateField} placeholder="Minutes per day" /></div>
          </div>
          <label htmlFor="projects-experience">Projects or experience <span>Optional</span></label>
          <textarea id="projects-experience" name="projectsExperience" rows="4" maxLength="8000" value={form.projectsExperience} onChange={updateField} placeholder="Share relevant work, projects, internships, or experience." />
          {error && <p className="form-error" role="alert">{error}</p>}
          <button className="primary-button form-submit" type="submit" disabled={isSubmitting}>{isSubmitting ? 'Analyzing…' : 'Analyze Opportunity'} <span aria-hidden="true">{isSubmitting ? '…' : '↗'}</span></button>
          <p className="form-note">Your information is sent to the configured AI service to prepare this report.</p>
        </form>
      </div>
      {report && <AnalysisReport report={report} />}
    </main>
  )
}

export default OpportunityInputPage
