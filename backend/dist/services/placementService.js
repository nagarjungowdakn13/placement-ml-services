"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.predictPlacement = void 0;
const axios_1 = __importDefault(require("axios"));
const rawPlacementUrl = process.env.PLACEMENT_SERVICE_URL;
const PLACEMENT_BASE_URL = rawPlacementUrl
    ? rawPlacementUrl.startsWith("http")
        ? rawPlacementUrl
        : `http://${rawPlacementUrl}`
    : "http://localhost:8003";
const predictPlacement = async (skills) => {
    const response = await axios_1.default.post(`${PLACEMENT_BASE_URL}/predict-placement`, { skills }, { timeout: 5000 });
    return response.data.placement_probability;
};
exports.predictPlacement = predictPlacement;
