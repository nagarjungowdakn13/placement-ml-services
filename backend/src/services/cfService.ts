import axios from "axios";

const rawCfUrl = process.env.CF_SERVICE_URL;
const CF_BASE_URL = rawCfUrl
  ? rawCfUrl.startsWith("http")
    ? rawCfUrl
    : `http://${rawCfUrl}`
  : "http://localhost:8002";

export const getJobRecommendations = async (skills: string[], topN: number) => {
  const response = await axios.post(
    `${CF_BASE_URL}/recommendations?top_n=${topN}`,
    { skills },
    { timeout: 5000 }
  );
  return response.data.recommendations as string[];
};
