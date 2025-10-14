import axios from "axios";
import { useEffect, useState } from "react";

const PlacementPrediction = ({ skills = [] }) => {
  const [prob, setProb] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [attempted, setAttempted] = useState(false);

  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
  useEffect(() => {
    const features = {
      cgpa: 8.5,
      dept: "CSE",
      projects: 3,
      internships: 1,
      aptitude_score: 85,
      interview_score: 80,
      skill_count: skills.length || 0,
    };
    const fetchPrediction = async () => {
      try {
        setAttempted(true);
        setLoading(true);
        setError("");
        if (!skills.length) {
          setProb(null);
          setLoading(false);
          return;
        }
        const res = await axios.post(`${API}/api/placement`, { skills });
        setProb(res.data.placement_probability);
      } catch (e) {
        setError("Failed to predict placement");
      } finally {
        setLoading(false);
      }
    };
    fetchPrediction();
  }, [JSON.stringify(skills)]);

  const percent = prob != null ? Math.round(prob * 100) : 0;
  return (
    <div className="prob-wrapper">
      {loading && (
        <div
          className="skeleton skel-line"
          style={{ height: 40, borderRadius: 8 }}
        />
      )}
      {attempted && error && (
        <p style={{ color: "var(--color-danger)", fontSize: ".85rem" }}>
          {error}
        </p>
      )}
      {!loading && !error && prob != null && (
        <div className="fade-in">
          <div className="progress" aria-label="Placement probability progress">
            <span style={{ width: percent + "%" }} />
          </div>
          <div
            className="prob-value"
            aria-live="polite"
            aria-label="Placement probability value"
          >
            {percent}%
          </div>
        </div>
      )}
      {!loading && !error && prob == null && (
        <div className="empty">
          Extract or add skills to see an estimated probability.
        </div>
      )}
    </div>
  );
};

export default PlacementPrediction;
