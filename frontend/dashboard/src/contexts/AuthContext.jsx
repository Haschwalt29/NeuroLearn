import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import toast from 'react-hot-toast'

// Set base URL for production
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://neurolearn-6c0k.onrender.com'
axios.defaults.baseURL = API_BASE_URL

const AuthContext = createContext()

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(null)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      axios.defaults.headers.common['Authorization'] = `Bearer ${storedToken}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [])

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      localStorage.removeItem('token')
      setToken(null)
      delete axios.defaults.headers.common['Authorization']
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await axios.post('/api/auth/login', { email, password })
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setUser(userData)
      
      toast.success('Welcome back!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const signup = async (email, password, name, role = 'learner') => {
    try {
      const response = await axios.post('/api/auth/signup', { 
        email, 
        password, 
        name, 
        role 
      })
      const { access_token, user: userData } = response.data
      
      localStorage.setItem('token', access_token)
      setToken(access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      setUser(userData)
      
      toast.success('Account created successfully!')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Signup failed'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
    toast.success('Logged out successfully')
  }

  const updateUser = (updates) => {
    setUser(prev => ({ ...prev, ...updates }))
  }

  const value = {
    user,
    token,
    loading,
    login,
    signup,
    logout,
    updateUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
