/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        emotion: {
          happy: '#10b981',
          sad: '#3b82f6',
          angry: '#ef4444',
          fear: '#8b5cf6',
          surprise: '#f59e0b',
          disgust: '#84cc16',
          neutral: '#6b7280'
        }
      },
      animation: {
        'pulse-emotion': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounce 1s infinite',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        }
      }
    },
  },
  plugins: [],
}
