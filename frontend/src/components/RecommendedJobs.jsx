import axios from "axios";
import { useEffect, useState } from "react";

const RecommendedJobs = ({ studentId }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await axios.get(`${API}/api/jobs/recommend/${studentId}`);
        setJobs(res.data.recommendations || []);
      } catch (e) {
        setError("Failed to load recommendations");
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, [studentId]);
  return (
    <div>
      <h2>Recommended Jobs</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && (
        <ul>
          {jobs.map((job, i) => (
            <li key={i}>{job}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RecommendedJobs;
