import axios from "axios";

const CF_BASE_URL = process.env.CF_SERVICE_URL || "http://localhost:8002";

export const getJobRecommendations = async (skills: string[], topN: number) => {
  const response = await axios.post(
    `${CF_BASE_URL}/recommendations?top_n=${topN}`,
    { skills },
    { timeout: 5000 }
  );
  return response.data.recommendations as string[];
};
