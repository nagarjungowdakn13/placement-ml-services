import { Request, Response, Router } from "express";
import multer from "multer";
import { parseResumeBuffer } from "../services/nlpService";

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

// Guidance for browser GETs
router.get("/upload", (_req: Request, res: Response) => {
  res.status(405).json({
    error: "Method Not Allowed",
    message:
      "Use POST /api/resumes/upload with multipart/form-data and field name 'resume'",
  });
});

router.post(
  "/upload",
  upload.single("resume"),
  async (req: Request, res: Response) => {
    if (!req.file) return res.status(400).json({ error: "No file uploaded" });
    try {
      const skills = await parseResumeBuffer(
        req.file.buffer,
        req.file.originalname
      );
      res.json({ skills });
    } catch (err) {
      const message =
        (err as any)?.response?.data ||
        (err as Error)?.message ||
        "Failed to parse resume";
      res
        .status(500)
        .json({ error: "Failed to parse resume", details: message });
    }
  }
);

export default router;
