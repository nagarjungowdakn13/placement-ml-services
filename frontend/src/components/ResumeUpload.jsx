import axios from "axios";
import { useState } from "react";

const ResumeUpload = () => {
  const [skills, setSkills] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

  const handleUpload = async () => {
    if (!file) return;
    try {
      setLoading(true);
      setError("");
      const formData = new FormData();
      formData.append("resume", file);
      const res = await axios.post(`${API}/api/resumes/upload`, formData);
      setSkills(res.data.skills || []);
    } catch (e) {
      setError("Failed to upload or parse resume");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Upload Resume</h2>
      <input type="file" onChange={(e) => setFile(e.target.files[0])} />
      <button onClick={handleUpload} disabled={loading}>
        {loading ? "Uploading..." : "Upload"}
      </button>
      {error && <p style={{ color: "red" }}>{error}</p>}
      {skills.length > 0 && (
        <ul>
          {skills.map((s, i) => (
            <li key={i}>{s}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ResumeUpload;
