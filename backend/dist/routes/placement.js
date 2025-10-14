"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const placementService_1 = require("../services/placementService");
const router = (0, express_1.Router)();
router.get("/", (_req, res) => {
    res.status(405).json({
        error: "Method Not Allowed",
        message: "Use POST /api/placement with JSON body of student features",
    });
});
router.post("/", async (req, res) => {
    try {
        const probability = await (0, placementService_1.predictPlacement)(req.body);
        res.json({ placement_probability: probability });
    }
    catch (err) {
        res.status(500).json({ error: "Failed to predict placement" });
    }
});
exports.default = router;
