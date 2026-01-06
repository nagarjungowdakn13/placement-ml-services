const Projects = ({ projects = [] }) => {
  if (!Array.isArray(projects) || projects.length === 0) {
    return (
      <div className="empty" style={{ marginTop: 12 }}>
        No projects in the resume.
      </div>
    );
  }

  return (
    <div style={{ marginTop: 4 }}>
      <ul style={{ marginTop: 8, paddingLeft: 0, listStyle: "none" }}>
        {projects.map((prj, idx) => (
          <li
            key={idx}
            className="card subtle"
            style={{ marginBottom: 10, padding: 12 }}
          >
            <div style={{ fontWeight: 600 }}>
              {prj?.title || "Untitled Project"}
            </div>
            {prj?.description ? (
              <div
                className="subtle"
                style={{ marginTop: 6, whiteSpace: "pre-wrap" }}
              >
                {prj.description}
              </div>
            ) : null}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Projects;
