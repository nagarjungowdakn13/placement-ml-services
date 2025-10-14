import { Request, Response, Router } from "express";
import { predictPlacement } from "../services/placementService";

const router = Router();

router.get("/", (_req: Request, res: Response) => {
  res.status(405).json({
    error: "Method Not Allowed",
    message: "Use POST /api/placement with JSON body of student features",
  });
});

router.post("/", async (req: Request, res: Response) => {
  try {
    const probability = await predictPlacement(req.body);
    res.json({ placement_probability: probability });
  } catch (err) {
    res.status(500).json({ error: "Failed to predict placement" });
  }
});

export default router;
