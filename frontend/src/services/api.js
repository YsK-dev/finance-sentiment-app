import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 60000, // 60 seconds for initial model loading
});

// Add error interceptor for better error handling
api.interceptors.response.use(
    response => response,
    error => {
        if (error.code === 'ERR_BLOCKED_BY_CLIENT') {
            console.error('Request blocked by browser extension (ad blocker). Please disable it for localhost.');
            error.message = 'Request blocked by browser extension. Please disable ad blocker for localhost.';
        } else if (error.code === 'ECONNABORTED') {
            error.message = 'Request timeout. Please try again.';
        } else if (!error.response) {
            error.message = 'Cannot connect to backend. Make sure the server is running on port 8000.';
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
