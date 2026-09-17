import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL 
    ? (import.meta.env.VITE_API_URL.endsWith('/') ? import.meta.env.VITE_API_URL.slice(0, -1) : import.meta.env.VITE_API_URL)
    : "https://ajeet-consumer-attention-mapping-system.onrender.com";

const api = axios.create({
    baseURL: baseURL,
});

// Flag to prevent multiple redirects
let isRedirecting = false;

// Request interceptor: attach JWT token and block requests if no token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem("token");
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        // If we're already redirecting to login, cancel this request
        if (isRedirecting) {
            const source = axios.CancelToken.source();
            config.cancelToken = source.token;
            source.cancel("Redirecting to login");
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor: on 401, clear token and redirect to login ONCE
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401 && !isRedirecting) {
            isRedirecting = true;
            localStorage.removeItem("token");
            window.location.href = "/";
        }
        return Promise.reject(error);
    }
);

export default api;