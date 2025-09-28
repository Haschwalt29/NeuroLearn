import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { EmotionProvider } from './contexts/EmotionContext'
import { SocketProvider } from './contexts/SocketContext'
import { ThemeProvider } from './contexts/ThemeContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import AdminDashboard from './pages/AdminDashboard'
import FeedbackPage from './pages/FeedbackPage'
import RevisionPage from './pages/RevisionPage'
import Navbar from './components/Navbar'
import LoadingSpinner from './components/LoadingSpinner'

function ProtectedRoute({ children, requireAdmin = false }) {
  const { user, loading } = useAuth()
  
  if (loading) return <LoadingSpinner />
  if (!user) return <Navigate to="/login" />
  if (requireAdmin && user.role !== 'teacher') return <Navigate to="/dashboard" />
  
  return children
}

function AppRoutes() {
  const { user } = useAuth()
  
  return (
    <Router>
      <div>
        {user && <Navbar />}
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" />} />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/feedback" 
            element={
              <ProtectedRoute>
                <FeedbackPage />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/settings" 
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/admin" 
            element={
              <ProtectedRoute requireAdmin>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/revision" 
            element={
              <ProtectedRoute>
                <RevisionPage />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/dashboard" />} />
        </Routes>
      </div>
    </Router>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <SocketProvider>
          <EmotionProvider>
            <AppRoutes />
            <Toaster 
              position="top-right"
              toastOptions={{
                className: 'dark:bg-gray-800 dark:text-white',
                style: {
                  background: 'var(--toast-bg)',
                  color: 'var(--toast-color)',
                },
              }}
            />
          </EmotionProvider>
        </SocketProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
