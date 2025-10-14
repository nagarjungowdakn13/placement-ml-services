import axios from "axios";

const CF_BASE_URL = process.env.CF_SERVICE_URL || "http://localhost:8002";

export const getJobRecommendations = async (
  studentId: string,
  topN: number
) => {
  const response = await axios.get(
    `${CF_BASE_URL}/recommendations/${studentId}?top_n=${topN}`,
    { timeout: 5000 }
  );
  return response.data.recommendations as string[];
};
