import axios from "axios";
import { useCallback, useState } from "react";

const ResumeUpload = ({ onExtracted }) => {
  const [skills, setSkills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [attempted, setAttempted] = useState(false);
  const [manualSkill, setManualSkill] = useState("");
  const API = import.meta.env.VITE_API_URL || "http://localhost:5000";

  const uploadFile = async (file) => {
    if (!file) return;
    try {
      setAttempted(true);
      setLoading(true);
      setError("");
      const formData = new FormData();
      formData.append("resume", file);
      const res = await axios.post(`${API}/api/resumes/upload`, formData);
      const s = (res.data.skills || []).sort();
      setSkills(s);
      onExtracted && onExtracted(s);
    } catch (e) {
      const details =
        e?.response?.data?.details ||
        e?.response?.data?.error ||
        e?.message ||
        "Failed to upload or parse resume";
      setError(typeof details === "string" ? details : JSON.stringify(details));
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const f = e.target.files?.[0];
    if (f) uploadFile(f);
  };

  const removeSkill = useCallback(
    (skill) => {
      const updated = skills.filter((s) => s !== skill);
      setSkills(updated);
      onExtracted && onExtracted(updated);
    },
    [skills, onExtracted]
  );

  const addManualSkill = () => {
    const val = manualSkill.trim();
    if (!val) return;
    const exists = skills.some((s) => s.toLowerCase() === val.toLowerCase());
    if (exists) {
      setManualSkill("");
      return;
    }
    const updated = [...skills, val].sort();
    setSkills(updated);
    onExtracted && onExtracted(updated);
    setManualSkill("");
    setAttempted(true);
  };

  const clearAll = () => {
    if (!skills.length) return;
    if (window.confirm("Clear all extracted/added skills?")) {
      setSkills([]);
      onExtracted && onExtracted([]);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={handleFileChange}
        aria-label="Upload resume file"
      />
      <div
        style={{
          marginTop: 12,
          display: "flex",
          gap: 8,
          alignItems: "center",
          flexWrap: "wrap",
        }}
      >
        <input
          type="text"
          placeholder="Add a skill manually"
          value={manualSkill}
          onChange={(e) => setManualSkill(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addManualSkill();
            }
          }}
          aria-label="Manual skill input"
        />
        <button
          className="button"
          onClick={addManualSkill}
          disabled={!manualSkill.trim()}
        >
          Add Skill
        </button>
        <button
          className="button outline"
          onClick={clearAll}
          disabled={!skills.length}
        >
          Clear All
        </button>
      </div>
      {loading && (
        <div
          className="skeleton"
          style={{ height: 46, marginTop: 16, borderRadius: 8 }}
        />
      )}
      {attempted && error && (
        <p style={{ color: "var(--color-danger)", fontSize: ".85rem" }}>
          {error}
        </p>
      )}
      {attempted && skills.length > 0 && (
        <div className="skill-chips fade-in" aria-label="Extracted skills list">
          {skills.map((s) => (
            <span className="chip" key={s}>
              {s}
              <button onClick={() => removeSkill(s)} aria-label={`Remove ${s}`}>
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      {attempted && !error && skills.length === 0 && !loading && (
        <div className="empty" style={{ marginTop: 12 }}>
          No skills detected. You can add them manually.
        </div>
      )}
    </div>
  );
};

export default ResumeUpload;
