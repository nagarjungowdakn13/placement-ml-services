import axios from "axios";
import FormData from "form-data";
import fs from "fs";

const rawNlpUrl = process.env.NLP_SERVICE_URL;
const NLP_BASE_URL = rawNlpUrl
  ? rawNlpUrl.startsWith("http")
    ? rawNlpUrl
    : `http://${rawNlpUrl}`
  : "http://localhost:8001";

export type ParsedResume = {
  skills: string[];
  projects?: { title: string; description: string }[];
};

export const parseResume = async (filePath: string): Promise<ParsedResume> => {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));

  const response = await axios.post(`${NLP_BASE_URL}/parse`, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    timeout: 30000,
  });
  return response.data as ParsedResume;
};

export const parseResumeBuffer = async (
  buffer: Buffer,
  filename: string
): Promise<ParsedResume> => {
  const form = new FormData();
  form.append("file", buffer, { filename });
  const response = await axios.post(`${NLP_BASE_URL}/parse`, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    timeout: 30000,
  });
  return response.data as ParsedResume;
};
