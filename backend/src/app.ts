import cors from "cors";
import "dotenv/config";
import express, { Request, Response } from "express";
import jobRoutes from "./routes/jobs";
import placementRoutes from "./routes/placement";
import resumeRoutes from "./routes/resumes";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api/resumes", resumeRoutes);
app.use("/api/jobs", jobRoutes);
app.use("/api/placement", placementRoutes);

const PORT = process.env.PORT || 5000;
app.get("/health", (_req: Request, res: Response) =>
  res.json({ status: "ok" })
);
app.listen(PORT, () => console.log(`Backend running on port ${PORT}`));
export default app;
