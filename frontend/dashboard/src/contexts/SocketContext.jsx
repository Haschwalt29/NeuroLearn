import React, { createContext, useContext, useEffect, useState } from 'react'
import { io } from 'socket.io-client'
import { useAuth } from './AuthContext'

const SocketContext = createContext()

export function useSocket() {
  const context = useContext(SocketContext)
  if (!context) {
    throw new Error('useSocket must be used within a SocketProvider')
  }
  return context
}

export function SocketProvider({ children }) {
  const [socket, setSocket] = useState(null)
  const [connected, setConnected] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      const newSocket = io(import.meta.env.VITE_API_BASE_URL || '', {
        auth: {
          token: localStorage.getItem('token')
        }
      })

      newSocket.on('connect', () => {
        setConnected(true)
        console.log('Connected to server')
      })

      newSocket.on('disconnect', () => {
        setConnected(false)
        console.log('Disconnected from server')
      }) 

      newSocket.on('connect_error', (error) => {
        console.error('Connection error:', error)
        setConnected(false)
      })

      setSocket(newSocket)

      return () => {
        newSocket.close()
      }
    } else {
      if (socket) {
        socket.close()
        setSocket(null)
        setConnected(false)
      }
    }
  }, [user])

  const emit = (event, data) => {
    if (socket && connected) {
      socket.emit(event, data)
    }
  }

  const on = (event, callback) => {
    if (socket) {
      socket.on(event, callback)
    }
  }

  const off = (event, callback) => {
    if (socket) {
      socket.off(event, callback)
    }
  }

  const value = {
    socket,
    connected,
    emit,
    on,
    off
  }

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  )
}
