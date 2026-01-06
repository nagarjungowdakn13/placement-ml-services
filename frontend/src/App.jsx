import { useEffect, useState } from "react";
import PlacementPrediction from "./components/PlacementPrediction";
import Projects from "./components/Projects";
import RecommendedJobs from "./components/RecommendedJobs";
import ResumeUpload from "./components/ResumeUpload";

function App() {
  const [skills, setSkills] = useState([]);
  const [projects, setProjects] = useState([]);
  const [dark, setDark] = useState(() => {
    try {
      return localStorage.getItem("theme") === "dark";
    } catch {
      return false;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (dark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    try {
      localStorage.setItem("theme", dark ? "dark" : "light");
    } catch {}
  }, [dark]);

  return (
    <div className="container">
      <header className="app-header">
        <div>
          <h1>Placement Dashboard</h1>
          <div className="subtle">
            Resume skill extraction, job recommendations & placement probability
          </div>
        </div>
        <button
          className="button outline theme-toggle"
          onClick={() => setDark((d) => !d)}
          aria-label="Toggle theme"
        >
          {dark ? "🌞 Light" : "🌙 Dark"}
        </button>
      </header>
      <div className="grid grid-cols-2" style={{ alignItems: "stretch" }}>
        <div className="card" style={{ gridColumn: "1 / -1" }}>
          <h2>Resume & Skills</h2>
          <ResumeUpload
            onExtracted={setSkills}
            onParsed={({ skills, projects }) => {
              setSkills(skills || []);
              setProjects(projects || []);
            }}
          />
        </div>
        <div className="card">
          <h2>Recommended Jobs</h2>
          <RecommendedJobs skills={skills} />
        </div>
        <div className="card">
          <h2>Placement Probability</h2>
          <PlacementPrediction skills={skills} />
        </div>
        <div className="card">
          <h2>Projects</h2>
          <Projects projects={projects} />
        </div>
      </div>
    </div>
  );
}

export default App;
