// API is always accessed via /api path (nginx routes this to backend)
export const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost/api';
