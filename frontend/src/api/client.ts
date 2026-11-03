import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL?.replace(/\/+$/, '')

export const api = axios.create({ baseURL: `${apiUrl ?? ''}/api/v1` })

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail) && detail.length
        ? detail.map((item) => `${item.loc?.slice(1).join('.')}: ${item.msg}`).join(', ')
        : 'Error de comunicación con el servidor'
    return Promise.reject(new Error(message))
  },
)
