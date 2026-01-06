"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const cfService_1 = require("../services/cfService");
const router = (0, express_1.Router)();
router.post("/recommend", async (req, res) => {
    try {
        const skills = Array.isArray(req.body?.skills)
            ? req.body.skills
            : [];
        const topN = Number(req.query.top_n) || 5;
        if (!skills.length)
            return res.status(400).json({ error: "skills array required" });
        const recommendations = await (0, cfService_1.getJobRecommendations)(skills, topN);
        res.json({ recommendations });
    }
    catch (err) {
        res.status(500).json({ error: "Failed to fetch recommendations" });
    }
});
exports.default = router;
