"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.predictPlacement = void 0;
const axios_1 = __importDefault(require("axios"));
const PLACEMENT_BASE_URL = process.env.PLACEMENT_SERVICE_URL || "http://localhost:8003";
const predictPlacement = async (studentFeatures) => {
    const response = await axios_1.default.post(`${PLACEMENT_BASE_URL}/predict-placement`, studentFeatures, { timeout: 5000 });
    return response.data.placement_probability;
};
exports.predictPlacement = predictPlacement;
