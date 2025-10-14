"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const cfService_1 = require("../services/cfService");
const router = (0, express_1.Router)();
router.get("/recommend/:studentId", async (req, res) => {
    try {
        const studentId = req.params.studentId;
        const topN = Number(req.query.top_n) || 5;
        const recommendations = await (0, cfService_1.getJobRecommendations)(studentId, topN);
        res.json({ recommendations });
    }
    catch (err) {
        res.status(500).json({ error: "Failed to fetch recommendations" });
    }
});
exports.default = router;
