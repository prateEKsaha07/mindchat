import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000'

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.authorization = `Bearer ${token}`
  }
  return config
})

export const registerUser = (username, email, password) =>
  api.post('/auth/register', { username, email, password })

export const loginUser = (email, password) =>
  api.post('/auth/login', { email, password })

export const getMe = () =>
  api.get('/auth/me')

export const sendMessage = (message, conversation_id = null) =>
  api.post('/chat/', { message, conversation_id })

export const getConversations = () =>
  api.get('/chat/conversations')

export const getMessages = (conversation_id) =>
  api.get(`/chat/conversations/${conversation_id}/messages`)

export const streamMessage = async (message, conversation_id = null, onToken, onDone) => {
  const token = localStorage.getItem('token')

  const response = await fetch(`${BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ message, conversation_id })
  })

  // Read conversation ID from response header
  const conversationId = response.headers.get('X-Conversation-Id') || conversation_id

  const reader = response.body.getReader()
  const decoder = new TextDecoder()

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    const chunk = decoder.decode(value)
    onToken(chunk)
  }

  onDone(conversationId)
}

export default api