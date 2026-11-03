import axios from 'axios'

export const api = axios.create({ baseURL: `${import.meta.env.VITE_API_URL ?? ''}/api/v1` })

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail ?? 'Error de comunicación con el servidor'
    return Promise.reject(new Error(typeof message === 'string' ? message : 'Error de validación'))
  },
)
