import axios from "axios";
import { useEffect, useState } from "react";

const PlacementPrediction = ({ studentId }) => {
  const [prob, setProb] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";
  useEffect(() => {
    const features = {
      cgpa: 8.5,
      dept: "CSE",
      projects: 3,
      internships: 1,
      aptitude_score: 85,
      interview_score: 80,
      skill_count: 5,
    };
    const fetchPrediction = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await axios.post(`${API}/api/placement`, features);
        setProb(res.data.placement_probability);
      } catch (e) {
        setError("Failed to predict placement");
      } finally {
        setLoading(false);
      }
    };
    fetchPrediction();
  }, [studentId]);

  return (
    <div>
      <h2>Placement Probability</h2>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: "red" }}>{error}</p>}
      {!loading && !error && prob !== null && <p>{prob * 100}%</p>}
    </div>
  );
};

export default PlacementPrediction;
