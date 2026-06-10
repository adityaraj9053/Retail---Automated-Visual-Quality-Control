

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000/api`;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── API Functions ────────────────────────────────────────

/** Health check */
export const getHealth = () => api.get('/health');

/** Upload image for prediction */
export const predictImage = (formData: FormData) =>
  api.post('/predict', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

/** Send webcam frame for prediction */
export const predictWebcamFrame = (frameBlob: Blob) => {
  const form = new FormData();
  form.append('frame', frameBlob);
  return api.post('/webcam/predict', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

/** Get analytics data */
export const getAnalytics = () => api.get('/analytics');

/** Get prediction history */
export const getHistory = (page = 1, limit = 20) =>
  api.get(`/history?page=${page}&limit=${limit}`);


export const getSystemMetrics = () => api.get('/system/metrics');

/** Submit operator feedback (Human-in-the-Loop) */
export const submitFeedback = (predictionId: number, correctedLabel: string, notes?: string) =>
  api.post('/feedback', { prediction_id: predictionId, corrected_label: correctedLabel, notes });

export default api;
