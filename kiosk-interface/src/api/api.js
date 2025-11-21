// src/services/api.js
import axios from 'axios'

// Change this to match your backend URL
const api = axios.create({
  baseURL: 'http://172.20.10.5:8000', // FastAPI backend
  timeout: 10000,
})

export default api
