import { Request, Response, Router } from "express";
import { predictPlacement } from "../services/placementService";

const router = Router();

router.get("/", (_req: Request, res: Response) => {
  res.status(405).json({
    error: "Method Not Allowed",
    message: "Use POST /api/placement with JSON body { skills: string[] }",
  });
});

router.post("/", async (req: Request, res: Response) => {
  try {
    const skills: string[] = Array.isArray(req.body?.skills)
      ? req.body.skills
      : [];
    if (!skills.length)
      return res.status(400).json({ error: "skills array required" });
    const probability = await predictPlacement(skills);
    res.json({ placement_probability: probability });
  } catch (err) {
    res.status(500).json({ error: "Failed to predict placement" });
  }
});

export default router;
