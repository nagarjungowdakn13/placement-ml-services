import { Router } from "express";
import { getJobRecommendations } from "../services/cfService";

const router = Router();

router.get("/recommend/:studentId", async (req, res) => {
  try {
    const studentId = req.params.studentId;
    const topN = Number(req.query.top_n) || 5;
    const recommendations = await getJobRecommendations(studentId, topN);
    res.json({ recommendations });
  } catch (err) {
    res.status(500).json({ error: "Failed to fetch recommendations" });
  }
});

export default router;
