import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { getConversations, getMessages } from '../services/api'
import { streamMessage } from '../services/api'

function Chat() {
  const [conversations, setConversations] = useState([])
  const [currentConversationId, setCurrentConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const messagesEndRef = useRef(null)
  const navigate = useNavigate()

  const user = JSON.parse(localStorage.getItem('user') || '{}')

  // Auto scroll to bottom when messages update
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const res = await getConversations()
      setConversations(res.data)
    } catch (err) {
      console.error('Failed to load conversations', err)
    }
  }

  const loadMessages = async (conversationId) => {
    try {
      const res = await getMessages(conversationId)
      setMessages(res.data)
      setCurrentConversationId(conversationId)
    } catch (err) {
      console.error('Failed to load messages', err)
    }
  }

  const startNewChat = () => {
    setCurrentConversationId(null)
    setMessages([])
    setInput('')
  }

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setLoading(true)
    setStreamingText('')

    // Add user message to UI immediately
    // without waiting for the server
    setMessages(prev => [...prev, {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      created_at: new Date().toISOString()
    }])

    try {
      let fullResponse = ''

      await streamMessage(
        userMessage,
        currentConversationId,

        // onToken — called for every token that arrives
        (token) => {
          fullResponse += token
          setStreamingText(fullResponse)
        },

        // onDone — called when stream is complete
        (conversationId) => {
          // Add the complete assistant message to messages
          setMessages(prev => [...prev, {
            id: Date.now() + 1,
            role: 'assistant',
            content: fullResponse,
            created_at: new Date().toISOString()
          }])

          // Clear the streaming text
          setStreamingText('')

          // Update conversation ID if this was a new chat
          if (!currentConversationId) {
            setCurrentConversationId(conversationId)
            loadConversations()  // refresh sidebar
          }
        }
      )
    } catch (err) {
      console.error('Stream error', err)
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
        created_at: new Date().toISOString()
      }])
      setStreamingText('')
    } finally {
      setLoading(false)
    }
  }

  // Send on Enter key
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-gray-950 text-white">

      {/* ── Sidebar ── */}
      <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">

        {/* Sidebar header */}
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-bold text-white">MindChat</h1>
          <p className="text-xs text-gray-400 mt-1">Hi, {user.username}</p>
        </div>

        {/* New chat button */}
        <div className="p-3">
          <button
            onClick={startNewChat}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-lg transition-colors"
          >
            + New Chat
          </button>
        </div>

        {/* Conversation list */}
        <div className="flex-1 overflow-y-auto px-3 space-y-1">
          {conversations.length === 0 && (
            <p className="text-gray-500 text-xs text-center mt-4">
              No conversations yet
            </p>
          )}
          {conversations.map(conv => (
            <button
              key={conv.id}
              onClick={() => loadMessages(conv.id)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors truncate ${
                currentConversationId === conv.id
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              {conv.title}
            </button>
          ))}
        </div>

        {/* Logout button */}
        <div className="p-3 border-t border-gray-800">
          <button
            onClick={handleLogout}
            className="w-full text-gray-400 hover:text-white text-sm py-2 px-4 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Logout
          </button>
        </div>
      </div>

      {/* ── Main chat area ── */}
      <div className="flex-1 flex flex-col">

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">

          {/* Empty state */}
          {messages.length === 0 && !streamingText && (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <h2 className="text-2xl font-bold text-white mb-2">
                What can I help you with?
              </h2>
              <p className="text-gray-400 text-sm">
                Ask me anything — I'm here to help.
              </p>
            </div>
          )}

          {/* Message bubbles */}
          {messages.map(msg => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-sm'
                  : 'bg-gray-800 text-gray-100 rounded-bl-sm'
              }`}>
                {msg.content}
              </div>
            </div>
          ))}

          {/* Streaming text — shows while model is generating */}
          {streamingText && (
            <div className="flex justify-start">
              <div className="max-w-2xl px-4 py-3 rounded-2xl rounded-bl-sm text-sm leading-relaxed bg-gray-800 text-gray-100">
                {streamingText}
                {/* Blinking cursor while streaming */}
                <span className="inline-block w-1 h-4 bg-blue-400 ml-1 animate-pulse" />
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* ── Input area ── */}
        <div className="border-t border-gray-800 px-6 py-4">
          <div className="flex gap-3 items-end max-w-4xl mx-auto">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Message MindChat..."
              rows={1}
              disabled={loading}
              className="flex-1 bg-gray-800 text-white rounded-xl px-4 py-3 border border-gray-700 focus:outline-none focus:border-blue-500 resize-none transition-colors disabled:opacity-50 text-sm"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white px-4 py-3 rounded-xl transition-colors"
            >
              {loading ? '...' : '↑'}
            </button>
          </div>
          <p className="text-center text-gray-600 text-xs mt-2">
            Press Enter to send · Shift+Enter for new line
          </p>
        </div>
      </div>
    </div>
  )
}

export default Chat