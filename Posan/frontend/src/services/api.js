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

// Homework / AI Study API - Multi-Agent System
export const homeworkAPI = {
    // NEW: Multi-Agent Workflow (One-click: Upload → Questions → Grading)
    uploadAndGeneratePractice: (formData, subject, grade, questionCount = 10, onUploadProgress = null) => {
        formData.append('subject', subject);
        formData.append('grade', grade);
        formData.append('question_count', questionCount);
        formData.append('question_types', 'mcq,short_answer');
        formData.append('difficulty', 'medium');
        formData.append('user_id', localStorage.getItem('user_id') || 'guest');
        return api.post('/homework-agents/workflow/material-to-practice', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            ...(onUploadProgress && { onUploadProgress }),
        });
    },

    // NEW: Upload and process material (Phase 1: Ingestion)
    uploadStudyMaterial: (formData, subject, grade, topic = '') => {
        formData.append('subject', subject);
        formData.append('grade', grade);
        if (topic) formData.append('topic', topic);
        formData.append('user_id', localStorage.getItem('user_id') || 'guest');
        return api.post('/homework-agents/materials/upload-v2', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    // NEW: Generate questions from context (Phase 3: Question Generator)
    generatePracticeQuestions: (context, subject, grade, count = 5, difficulty = 'medium') => {
        const formData = new FormData();
        formData.append('context', context);
        formData.append('subject', subject);
        formData.append('grade', grade);
        formData.append('question_types', 'mcq,short_answer');
        formData.append('count', count);
        formData.append('difficulty', difficulty);
        return api.post('/homework-agents/questions/generate', formData);
    },

    // NEW: Generate questions from indexed material (Phase 2 + 3)
    generateQuestionsFromMaterial: (indexName, topic, subject, grade, count = 5) => {
        const formData = new FormData();
        formData.append('index_name', indexName);
        formData.append('topic', topic);
        formData.append('subject', subject);
        formData.append('grade', grade);
        formData.append('question_types', 'mcq,short_answer');
        formData.append('count', count);
        formData.append('difficulty', 'medium');
        return api.post('/homework-agents/questions/from-material', formData);
    },

    // NEW: Auto-grade exam (Phase 4: Exam Analysis)
    gradeExam: (questions, studentId = null, examId = null) => {
        const formData = new FormData();
        formData.append('questions', JSON.stringify(questions));
        if (studentId) formData.append('student_id', studentId);
        if (examId) formData.append('exam_id', examId);
        return api.post('/homework-agents/exams/grade', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },

    // NEW: Quick grade single question
    quickGradeQuestion: (questionType, question, studentAnswer, correctAnswer, options = null, expectedAnswer = null) => {
        const formData = new FormData();
        formData.append('question_type', questionType);
        formData.append('question', question);
        formData.append('student_answer', studentAnswer);
        formData.append('correct_answer', correctAnswer);
        if (options) formData.append('options', JSON.stringify(options));
        if (expectedAnswer) formData.append('expected_answer', expectedAnswer);
        return api.post('/homework-agents/exams/quick-grade', formData);
    },

    // NEW: Get available question types
    getQuestionTypes: () => api.get('/homework-agents/questions/types'),

    // NEW: Get grading information
    getGradingInfo: () => api.get('/homework-agents/exams/grading-info'),

    // NEW: Semantic search in materials
    searchMaterial: (indexName, query, topK = 5) => {
        const formData = new FormData();
        formData.append('index_name', indexName);
        formData.append('query', query);
        formData.append('top_k', topK);
        formData.append('min_score', '0.0');
        return api.post('/homework-agents/search/query', formData);
    },

    // NEW: List all search indices
    listIndices: () => api.get('/homework-agents/search/indices'),

    // NEW: Get agent status
    getAgentStatus: (agentName, limit = 10) =>
        api.get(`/homework-agents/agents/status/${agentName}?limit=${limit}`),

    // NEW: List all agents
    listAgents: () => api.get('/homework-agents/agents/list'),

    // Bulk Upload: Upload multiple files and generate practice questions
    bulkUploadAndGeneratePractice: (formData, subject, grade, questionCountPerFile = 5, onUploadProgress = null) => {
        formData.append('subject', subject);
        formData.append('grade', grade);
        formData.append('question_count', questionCountPerFile);
        formData.append('question_types', 'mcq,short_answer');
        formData.append('difficulty', 'medium');
        formData.append('user_id', localStorage.getItem('user_id') || 'guest');
        return api.post('/homework-agents/workflow/bulk-material-to-practice', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            ...(onUploadProgress && { onUploadProgress }),
        });
    },

    // LEGACY: Keep old endpoints for backward compatibility
    analyzeTestUpload: (formData, params) => api.post('/ai/analyze/test-upload', formData, { params }),

    // Bulk Test Analysis: Upload multiple test paper pages and get combined report
    bulkAnalyzeTestUpload: (formData, params) => api.post('/ai/analyze/test-bulk-upload', formData, { params }),

    // Assignment CRUD
    getAssignments: (userId, status = null) => {
        const params = { user_id: userId };
        if (status) params.status = status;
        return api.get('/homework-agents/assignments', { params });
    },

    createAssignment: (formData) => {
        return api.post('/homework-agents/assignments', formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
        });
    },

    updateAssignmentStatus: (assignmentId, status) => {
        const formData = new FormData();
        formData.append('status', status);
        return api.put(`/homework-agents/assignments/${assignmentId}/status`, formData);
    },

    deleteAssignment: (assignmentId) =>
        api.delete(`/homework-agents/assignments/${assignmentId}`),

    // Exam history
    getExamHistory: (userId, limit = 20) =>
        api.get(`/homework-agents/exams/history?user_id=${userId}&limit=${limit}`),

    getExamDetails: (examId) =>
        api.get(`/homework-agents/exams/${examId}/details`),

    // Stats for progress widget
    getHomeworkStats: (userId) =>
        api.get(`/homework-agents/stats?user_id=${userId}`),
};

export default api;
