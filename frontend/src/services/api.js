import axios from 'axios';

// Empty means same origin: the backend serves the built app, and `npm run dev` proxies /api to it.
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 120000, // the first request loads the FinBERT model
});

// Add error interceptor for better error handling
api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.data?.detail && typeof error.response.data.detail === 'string') {
            error.message = error.response.data.detail;
        } else if (error.code === 'ERR_BLOCKED_BY_CLIENT') {
            console.error('Request blocked by browser extension (ad blocker). Please disable it for localhost.');
            error.message = 'Request blocked by browser extension. Please disable ad blocker for localhost.';
        } else if (error.code === 'ECONNABORTED') {
            error.message = 'Request timeout. Please try again.';
        } else if (!error.response) {
            error.message = 'Cannot connect to the backend.';
        }
        return Promise.reject(error);
    }
);

export const analyzeSymbol = async (symbol) => {
    const response = await api.get(`/api/analysis/symbol/${symbol}`);
    return response.data;
};

export const getInvestmentAdvice = async (symbol) => {
    const response = await api.get(`/api/analysis/advice/${symbol}`);
    return response.data;
};

export const analyzeYouTubeVideo = async (videoId) => {
    const response = await api.post('/api/sentiment/youtube/transcript', {
        video_id: videoId,
        language: 'en'
    });
    return response.data;
};

export const analyzeTextSentiment = async (text) => {
    const response = await api.post('/api/sentiment/analyze', {
        text: text,
        source_type: 'news'
    });
    return response.data;
};

export const getNewsArticles = async (symbol) => {
    const response = await api.get(`/api/data/news/${symbol}`);
    return response.data;
};

export const getBlogPosts = async (symbol) => {
    const response = await api.get(`/api/data/blogs/${symbol}`);
    return response.data;
};

export default api;
