import React, { useState } from 'react'
import Editor from '@monaco-editor/react'
import { motion } from 'framer-motion'
import axios from 'axios'
import { useAuth } from '../contexts/AuthContext'
import { useSocket } from '../contexts/SocketContext'

const defaults = {
  python: 'print("Hello from Python!")',
  javascript: 'console.log("Hello from JavaScript!")',
}

export default function CodingSandbox() {
  const [language, setLanguage] = useState('python')
  const [code, setCode] = useState(defaults.python)
  const [output, setOutput] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')
  const [execMs, setExecMs] = useState(0)
  const [loading, setLoading] = useState(false)
  const { token } = useAuth()
  const { emit } = useSocket()

  const runCode = async () => {
    setLoading(true)
    setOutput('')
    setError('')
    setStatus('')
    try {
      const res = await axios.post('/api/sandbox/run', { language, code }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setOutput(res.data.output || '')
      setError(res.data.error || '')
      setStatus(res.data.status || '')
      setExecMs(res.data.exec_ms || 0)
      emit('quest_progress', { action: 'code_run', language, status: res.data.status })
    } catch (e) {
      setError(e?.response?.data?.error || e.message)
      setStatus('error')
    } finally {
      setLoading(false)
    }
  }

  const switchLang = (lang) => {
    setLanguage(lang)
    setCode(defaults[lang])
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <div className="bg-gray-100 rounded-lg p-1">
          <button onClick={() => switchLang('python')} className={`px-3 py-1 rounded-md text-sm ${language==='python' ? 'bg-white shadow' : ''}`}>Python</button>
          <button onClick={() => switchLang('javascript')} className={`px-3 py-1 rounded-md text-sm ${language==='javascript' ? 'bg-white shadow' : ''}`}>JavaScript</button>
        </div>
        <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }} onClick={runCode}
          className="px-4 py-2 rounded-lg font-medium transition-all bg-blue-600 text-white" disabled={loading}>
          {loading ? 'Running…' : 'Run Code'}
        </motion.button>
        {status && (
          <span className={`text-sm ${status==='success' ? 'text-green-600' : status==='timeout' ? 'text-yellow-600' : 'text-red-600'}`}>
            {status.toUpperCase()} {execMs ? `(${execMs} ms)` : ''}
          </span>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="border rounded-lg overflow-hidden">
          <Editor
            height="360px"
            defaultLanguage={language}
            language={language}
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || '')}
            options={{ fontSize: 14, minimap: { enabled: false }, wordWrap: 'on' }}
          />
        </div>
        <div className="border rounded-lg bg-gray-50 p-3">
          <div className="text-xs text-gray-500 mb-2">Program Output</div>
          <pre className="text-sm whitespace-pre-wrap break-words">{output || ' '}</pre>
          {error && (
            <div className="mt-3">
              <div className="text-xs text-gray-500 mb-1">Errors</div>
              <pre className="text-sm text-red-700 whitespace-pre-wrap break-words">{error}</pre>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


