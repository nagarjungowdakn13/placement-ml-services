import axios from "axios";
import { useEffect, useState } from "react";

const RecommendedJobs = ({ skills = [] }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [attempted, setAttempted] = useState(false);
  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setAttempted(true);
        setLoading(true);
        setError("");
        if (!skills.length) {
          setJobs([]);
          setLoading(false);
          return;
        }
        const res = await axios.post(`${API}/api/jobs/recommend`, { skills });
        setJobs(res.data.recommendations || []);
      } catch (e) {
        setError("Failed to load recommendations");
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, [JSON.stringify(skills)]);
  const Skeleton = () => (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: 10,
        marginTop: 12,
      }}
    >
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="skeleton skel-line"
          style={{ height: 40, borderRadius: 8 }}
        />
      ))}
    </div>
  );

  return (
    <div>
      {loading && <Skeleton />}
      {attempted && error && (
        <p style={{ color: "var(--color-danger)", fontSize: ".85rem" }}>
          {error}
        </p>
      )}
      {!loading && !error && jobs.length > 0 && (
        <ul className="job-list fade-in" aria-label="Recommended job list">
          {jobs.map((job, i) => (
            <li className="job-item" key={job + "-" + i}>
              <span>{job}</span>
              <span className="badge">MATCH</span>
            </li>
          ))}
        </ul>
      )}
      {!loading &&
        !error &&
        attempted &&
        skills.length > 0 &&
        jobs.length === 0 && (
          <div className="empty">
            No matching jobs found. Try adding more relevant skills manually.
          </div>
        )}
      {!loading && !error && skills.length === 0 && (
        <div className="empty">Add or extract skills to see tailored jobs.</div>
      )}
    </div>
  );
};

export default RecommendedJobs;
