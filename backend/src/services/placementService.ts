import axios from "axios";

const PLACEMENT_BASE_URL =
  process.env.PLACEMENT_SERVICE_URL || "http://localhost:8003";

export const predictPlacement = async (studentFeatures: any) => {
  const response = await axios.post(
    `${PLACEMENT_BASE_URL}/predict-placement`,
    studentFeatures,
    { timeout: 5000 }
  );
  return response.data.placement_probability as number;
};
