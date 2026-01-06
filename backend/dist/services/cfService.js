"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getJobRecommendations = void 0;
const axios_1 = __importDefault(require("axios"));
const rawCfUrl = process.env.CF_SERVICE_URL;
const CF_BASE_URL = rawCfUrl
    ? rawCfUrl.startsWith("http")
        ? rawCfUrl
        : `http://${rawCfUrl}`
    : "http://localhost:8002";
const getJobRecommendations = async (skills, topN) => {
    const response = await axios_1.default.post(`${CF_BASE_URL}/recommendations?top_n=${topN}`, { skills }, { timeout: 5000 });
    return response.data.recommendations;
};
exports.getJobRecommendations = getJobRecommendations;
