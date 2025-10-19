import axios from 'axios'

const API_BASE_URL = 'http://127.0.0.1:8000'

export async function fetchResidents(params = {}) {
  try {
    const response = await axios.get(`${API_BASE_URL}/residents`, { params })
    return response.data
  } catch (error) {
    console.error('Error fetching residents:', error)
    throw error
  }
}

export async function fetchPuroks() {
  const { data } = await axios.get(`${API_BASE_URL}/residents/puroks`)
  return data
}