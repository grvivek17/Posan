import axios from 'axios';

// Use environment variable or fallback to localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Clear tokens and redirect to login
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// Auth API
export const authAPI = {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
    createParentAccount: (userId, data) => api.post(`/auth/parent-account?user_id=${userId}`, data),
};

// Users API
export const usersAPI = {
    getCurrentUser: (userId) => api.get(`/users/me?user_id=${userId}`),
    createChildProfile: (parentUserId, childUserId, data) =>
        api.post(`/users/child-profile?parent_user_id=${parentUserId}&child_user_id=${childUserId}`, data),
    getChildProfiles: (parentUserId) => api.get(`/users/child-profiles?parent_user_id=${parentUserId}`),
    getChildProfile: (childId) => api.get(`/users/child-profile/${childId}`),
    updateChildProfile: (childId, data) => api.put(`/users/child-profile/${childId}`, data),
};

// Content API
export const contentAPI = {
    getMagazines: (params) => api.get('/content/magazines', { params }),
    getMagazine: (id) => api.get(`/content/magazines/${id}`),
    getArticles: (params) => api.get('/content/articles', { params }),
    getArticle: (id) => api.get(`/content/articles/${id}`),
    submitQuiz: (userId, data) => api.post(`/content/quizzes/submit?user_id=${userId}`, data),
};

// Puzzles API
export const puzzlesAPI = {
    getPuzzles: (params) => api.get('/puzzles/puzzles', { params }),
    getPuzzle: (id) => api.get(`/puzzles/puzzles/${id}`),
    submitPuzzle: (userId, data) => api.post(`/puzzles/puzzles/submit?user_id=${userId}`, data),
    getUserProgress: (userId) => api.get(`/puzzles/puzzles/progress/${userId}`),
    getPuzzleStats: (userId) => api.get(`/puzzles/puzzles/stats/${userId}`),
    generateAIPuzzle: (params) => api.post('/puzzles/generate', null, { params }),
};

// Gamification API
export const gamificationAPI = {
    getBadges: () => api.get('/gamification/badges'),
    getUserAchievements: (userId) => api.get(`/gamification/achievements/${userId}`),
    getLeaderboard: (params) => api.get('/gamification/leaderboard', { params }),
    getUserStats: (userId) => api.get(`/gamification/stats/${userId}`),
};

// Homework / AI Study API
export const homeworkAPI = {
    uploadStudyMaterial: (formData, ageGroup) => api.post(`/ai/study-material/upload?age_group=${ageGroup}`, formData),
    generatePracticeQuestions: (params) => api.post('/ai/study-material/generate-questions', null, { params }),
    evaluateAnswer: (data) => api.post('/ai/study-material/evaluate-answer', data),
    analyzePerformance: (answers) => api.post('/ai/study-material/analyze-performance', answers),
    generateStudyPlan: (data) => api.post('/ai/study-material/generate-plan', data),
    analyzeTestUpload: (formData, params) => api.post('/ai/analyze/test-upload', formData, { params }),
};

export default api;
