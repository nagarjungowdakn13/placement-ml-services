import axios from "axios";
import FormData from "form-data";
import fs from "fs";

const NLP_BASE_URL = process.env.NLP_SERVICE_URL || "http://localhost:8001";

export const parseResume = async (filePath: string) => {
  const form = new FormData();
  form.append("file", fs.createReadStream(filePath));

  const response = await axios.post(`${NLP_BASE_URL}/parse`, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    timeout: 30000,
  });
  return response.data.skills as string[];
};

export const parseResumeBuffer = async (buffer: Buffer, filename: string) => {
  const form = new FormData();
  form.append("file", buffer, { filename });
  const response = await axios.post(`${NLP_BASE_URL}/parse`, form, {
    headers: form.getHeaders(),
    maxBodyLength: Infinity,
    timeout: 30000,
  });
  return response.data.skills as string[];
};
