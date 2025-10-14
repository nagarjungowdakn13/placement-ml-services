"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.parseResumeBuffer = exports.parseResume = void 0;
const axios_1 = __importDefault(require("axios"));
const form_data_1 = __importDefault(require("form-data"));
const fs_1 = __importDefault(require("fs"));
const NLP_BASE_URL = process.env.NLP_SERVICE_URL || "http://localhost:8001";
const parseResume = async (filePath) => {
    const form = new form_data_1.default();
    form.append("file", fs_1.default.createReadStream(filePath));
    const response = await axios_1.default.post(`${NLP_BASE_URL}/parse`, form, {
        headers: form.getHeaders(),
        maxBodyLength: Infinity,
        timeout: 10000,
    });
    return response.data.skills;
};
exports.parseResume = parseResume;
const parseResumeBuffer = async (buffer, filename) => {
    const form = new form_data_1.default();
    form.append("file", buffer, { filename });
    const response = await axios_1.default.post(`${NLP_BASE_URL}/parse`, form, {
        headers: form.getHeaders(),
        maxBodyLength: Infinity,
        timeout: 10000,
    });
    return response.data.skills;
};
exports.parseResumeBuffer = parseResumeBuffer;
