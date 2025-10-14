import { Router } from "express";
import { getJobRecommendations } from "../services/cfService";

const router = Router();

router.post("/recommend", async (req, res) => {
  try {
    const skills: string[] = Array.isArray(req.body?.skills)
      ? req.body.skills
      : [];
    const topN = Number(req.query.top_n) || 5;
    if (!skills.length)
      return res.status(400).json({ error: "skills array required" });
    const recommendations = await getJobRecommendations(skills, topN);
    res.json({ recommendations });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch recommendations" });
  }
});

export default router;
