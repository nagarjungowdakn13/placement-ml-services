"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const multer_1 = __importDefault(require("multer"));
const nlpService_1 = require("../services/nlpService");
const router = (0, express_1.Router)();
const upload = (0, multer_1.default)({ storage: multer_1.default.memoryStorage() });
// Guidance for browser GETs
router.get("/upload", (_req, res) => {
    res.status(405).json({
        error: "Method Not Allowed",
        message: "Use POST /api/resumes/upload with multipart/form-data and field name 'resume'",
    });
});
router.post("/upload", upload.single("resume"), async (req, res) => {
    if (!req.file)
        return res.status(400).json({ error: "No file uploaded" });
    try {
        const parsed = await (0, nlpService_1.parseResumeBuffer)(req.file.buffer, req.file.originalname);
        res.json({
            skills: parsed.skills || [],
            projects: parsed.projects || [],
        });
    }
    catch (err) {
        const message = err?.response?.data ||
            err?.message ||
            "Failed to parse resume";
        res
            .status(500)
            .json({ error: "Failed to parse resume", details: message });
    }
});
exports.default = router;
