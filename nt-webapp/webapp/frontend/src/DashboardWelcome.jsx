function DashboardWelcome() {
  return (
    <div className="welcome-container">
      <header className="welcome-header">
        <h1>NatureThrive: Bird Monitor</h1>
        <p className="welcome-tagline">Bird detection & biodiversity monitoring</p>
      </header>
      
      <main className="welcome-main">
        <div className="welcome-content">
          <h2>Welcome to the Dashboard</h2>
          <p>Track bird species, detect patterns, and understand biodiversity on your land using advanced acoustic monitoring technology.</p>
          
          <div className="welcome-features">
            <div className="feature">
              <h3>📊 Analytics</h3>
              <p>Detection counts and species diversity metrics</p>
            </div>
            <div className="feature">
              <h3>🐦 Species Tracking</h3>
              <p>Identify and monitor bird populations over time</p>
            </div>
            <div className="feature">
              <h3>🌍 Biodiversity Insights</h3>
              <p>Understand ecosystem health through acoustic data</p>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="welcome-footer">
        <button className="btn btn-primary" onClick={() => window.location.href = '/dashboard'}>
          View Dashboard
        </button>
        <button className="btn btn-secondary" onClick={() => window.open('https://naturethrive.co.uk/', '_blank')}>
          Back to naturethrive.co.uk
        </button>
      </footer>
    </div>
  );
}

export default DashboardWelcome;
