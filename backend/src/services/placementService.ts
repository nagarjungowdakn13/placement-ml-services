import axios from "axios";

const rawPlacementUrl = process.env.PLACEMENT_SERVICE_URL;
const PLACEMENT_BASE_URL = rawPlacementUrl
  ? rawPlacementUrl.startsWith("http")
    ? rawPlacementUrl
    : `http://${rawPlacementUrl}`
  : "http://localhost:8003";

export const predictPlacement = async (skills: string[]) => {
  const response = await axios.post(
    `${PLACEMENT_BASE_URL}/predict-placement`,
    { skills },
    { timeout: 5000 }
  );
  return response.data.placement_probability as number;
};
