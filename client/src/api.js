import axios from "axios";

const BASE = "http://127.0.0.1:8000";

export const splitText = (message) =>
  axios.post(`${BASE}/post/`, { message }).then((r) => r.data);

export const classify = (texts, labels, model) =>
  axios.post(`${BASE}/api/classify/`, { texts, labels, model }).then((r) => r.data);

export const sentiment = (texts, model) =>
  axios.post(`${BASE}/api/sentiment/`, { texts, model }).then((r) => r.data);

export const summarize = (texts, model) =>
  axios.post(`${BASE}/api/summarize/`, { texts, model }).then((r) => r.data);

export const keywords = (texts, model) =>
  axios.post(`${BASE}/api/keywords/`, { texts, model }).then((r) => r.data);

export const detectLanguage = (texts, model) =>
  axios.post(`${BASE}/api/language/`, { texts, model }).then((r) => r.data);

export const detectToxicity = (texts, model) =>
  axios.post(`${BASE}/api/toxicity/`, { texts, model }).then((r) => r.data);
