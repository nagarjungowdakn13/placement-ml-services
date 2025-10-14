import PlacementPrediction from "./components/PlacementPrediction";
import RecommendedJobs from "./components/RecommendedJobs";
import ResumeUpload from "./components/ResumeUpload";

function App() {
  return (
    <div>
      <h1>Placement Dashboard</h1>
      <ResumeUpload />
      <RecommendedJobs studentId="student1" />
      <PlacementPrediction studentId="student1" />
    </div>
  );
}

export default App;
