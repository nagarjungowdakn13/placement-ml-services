"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.getJobRecommendations = void 0;
const axios_1 = __importDefault(require("axios"));
const CF_BASE_URL = process.env.CF_SERVICE_URL || "http://localhost:8002";
const getJobRecommendations = async (studentId, topN) => {
    const response = await axios_1.default.get(`${CF_BASE_URL}/recommendations/${studentId}?top_n=${topN}`, { timeout: 5000 });
    return response.data.recommendations;
};
exports.getJobRecommendations = getJobRecommendations;
