# Frontend Documentation

## Architecture Overview

The NeuroLearn frontend is built with React 18 and follows modern best practices for component architecture, state management, and user experience design.

## Project Structure

```
frontend/dashboard/src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (buttons, forms, etc.)
│   ├── interactive/      # Interactive components (charts, 3D visualizations)
│   └── specific/        # Feature-specific components
├── pages/               # Main application pages/routes
├── hooks/               # Custom React hooks
├── contexts/            # React context providers
├── services/            # API service layers
├── utils/               # Utility functions
├── assets/              # Static assets (images, icons)
└── styles/              # Global styles and themes
```

## Component Architecture

### Component Hierarchy

#### Core Components
- **App**: Main application wrapper with routing and context providers
- **Layout**: Base layout component with navigation and sidebar
- **Dashboard**: Main dashboard view with analytics overview
- **TutorInterface**: Primary tutoring interface
- **EmotionDetection**: Real-time emotion detection component

#### Feature Components

##### Learning Components
- **AdaptiveTutor**: Main AI tutoring component
- **LearningDNA**: User learning profile visualization
- **KnowledgeGraph**: Interactive knowledge visualization with Three.js
- **SpacedRepetition**: Memory optimization interface

##### Gamification Components
- **QuestSystem**: Quest browsing and management
- **AchievementDashboard**: Badges and achievements display
- **ProgressBar**: Animated progress indicators
- **Leaderboard**: User ranking and competition

##### Emotion & Analytics
- **EmotionDetector**: Live camera emotion detection
- **AnalyticsDashboard**: Comprehensive performance metrics
- **ChartComponents**: Recharts-based data visualizations
- **PerformanceMetrics**: Detailed learning analytics

## State Management

### Zustand Stores

#### Core Stores
```javascript
// User authentication and profile
const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: async (credentials) => {...},
  logout: () => {...}
}));

// Learning session state
const useLearningStore = create((set) => ({
  currentSession: null,
  progress: {},
  startSession: (topic, difficulty) => {...},
  updateProgress: (progress) => {...}
}));

// Emotion detection state
const useEmotionStore = create((set) => ({
  currentEmotion: null,
  emotionHistory: [],
  isDetecting: false,
  startDetection: () => {...},
  stopDetection: () => {...}
}));
```

#### Feature-Specific Stores
- **GamificationStore**: Manages quests, badges, and achievements
- **AnalyticsStore**: Handles performance data and analytics
- **CollaborationStore**: Manages co-learning sessions

## Custom Hooks

### Utility Hooks
```javascript
// WebSocket connection management
function useWebSocket(url, options) {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  
  useEffect(() => {
    const ws = new WebSocket(url);
    setSocket(ws);
    return () => ws.close();
  }, [url]);
  
  return { socket, isConnected };
}

// Emotion detection hook
function useEmotionDetection() {
  const [stream, setStream] = useState(null);
  const [emotion, setEmotion] = useState(null);
  
  const startDetection = useCallback(async () => {
    const mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: true 
    });
    setStream(mediaStream);
  }, []);
  
  return { stream, emotion, startDetection };
}
```

### Business Logic Hooks
- **useTutoring**: Manages tutoring session state and interactions
- **useAnalytics**: Fetches and manages analytics data
- **useGamification**: Handles quest progress and achievements

## API Integration

### Service Layer Architecture
```javascript
// Base API service
class APIService {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }
  
  async request(endpoint, options = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }
    
    return response.json();
  }
}

// Feature-specific services
export const TutoringService = {
  async startSession(userId, topic, difficulty) {
    return apiService.request('/tutor/lesson', {
      method: 'POST',
      body: JSON.stringify({ userId, topic, difficulty })
    });
  },
  
  async submitResponse(sessionId, response) {
    return apiService.request(`/tutor/response/${sessionId}`, {
      method: 'POST',
      body: JSON.stringify({ response })
    });
  }
};
```

## Advanced UI Features

### 3D Visualizations (Three.js)
```javascript
// KnowledgeGraph3D Component
function KnowledgeGraph3D({ data }) {
  const { nodes, links } = data;
  
  return (
    <Canvas camera={{ position: [0, 0, 5] }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      {nodes.map((node, index) => (
        <Node3D
          key={node.id}
          position={[node.x, node.y, node.z]}
          data={node}
        />
      ))}
      
      {links.map((link, index) => (
        <Edge3D
          key={index}
          start={link.source}
          end={link.target}
          strength={link.strength}
        />
      ))}
    </Canvas>
  );
}
```

### Real-time Features (Socket.io)
```javascript
function useSocketConnection(url) {
  const [socket, setSocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  
  useEffect(() => {
    const newSocket = io(url);
    
    newSocket.on('connect', () => {
      setConnectionStatus('connected');
    });
    
    newSocket.on('disconnect', () => {
      setConnectionStatus('disconnected');
    });
    
    setSocket(newSocket);
    
    return () => newSocket.close();
  }, [url]);
  
  return { socket, connectionStatus };
}
```

## Performance Optimizations

### Code Splitting
```javascript
// Lazy loading heavy components
const KnowledgeGraph3D = lazy(() => import('./components/KnowledgeGraph3D'));
const AnalyticsDashboard = lazy(() => import('./components/AnalyticsDashboard'));

// Usage with Suspense
<Suspense fallback={<LoadingSpinner />}>
  <KnowledgeGraph3D data={knowledgeData} />
</Suspense>
```

### Memoization
```javascript
// Memoized components for expensive operations
const EmotionChart = React.memo(({ data, filters }) => {
  const processedData = useMemo(() => {
    return processEmotionData(data, filters);
  }, [data, filters]);
  
  return <ResponsiveContainer>{/* Chart content */}</ResponsiveContainer>;
});
```

### Virtual Scrolling
```javascript
// For large lists (emotion history, lesson logs)
import { FixedSizeList as List } from 'react-window';

const EmotionHistoryList = ({ emotions }) => (
  <List
    height={400}
    itemCount={emotions.length}
    itemSize={80}
  >
    {({ index, style }) => (
      <div style={style}>
        <EmotionItem emotion={emotions[index]} />
      </div>
    )}
  </List>
);
```

## Testing Strategy

### Component Testing
```javascript
// Example test for EmotionDetector component
import { render, screen, fireEvent } from '@testing-library/react';
import { EmotionDetector } from '../components/EmotionDetector';

describe('EmotionDetector', () => {
  it('should display emotion detection controls', () => {
    render(<EmotionDetector />);
    
    expect(screen.getByText('Start Detection')).toBeInTheDocument();
    expect(screen.getByText('Stop Detection')).toBeInTheDocument();
  });
  
  it('should handle emotion detection flow', async () => {
    const mockOnEmotionDetected = jest.fn();
    render(<EmotionDetector onEmotionDetected={mockOnEmotionDetected} />);
    
    fireEvent.click(screen.getByText('Start Detection'));
    
    // Mock emotion detection result
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100));
    });
    
    expect(mockOnEmotionDetected).toHaveBeenCalled();
  });
});
```

## Deployment Configuration

### Environment Variables
```bash
# Production environment
VITE_API_URL=https://api.neurolearn.com
VITE_WEBSOCKET_URL=wss://api.neurolearn.com/ws
VITE_SENTRY_DSN=your-sentry-dsn
VITE_GOOGLE_ANALYTICS_ID=GA-XXXXXX

# Development environment
VITE_API_URL=http://localhost:5000
VITE_WEBSOCKET_URL=ws://localhost:5000/ws
VITE_DEBUG_MODE=true
```

### Build Optimization
```javascript
// vite.config.js
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'd3'],
          three: ['three', '@react-three/fiber'],
          ui: ['framer-motion', 'lucide-react']
        }
      }
    }
  },
  optimizeDeps: {
    include: ['three', '@react-three/fiber', '@react-three/drei']
  }
});
```

## Accessibility Features

### ARIA Implementation
- Comprehensive screen reader support
- Keyboard navigation for all interactive elements
- Focus management for modal dialogs
- Descriptive alt text for images and charts

### WCAG Compliance
- AA level compliance with WCAG 2.1
- High contrast theme support
- Text scaling support
- Voice command integration

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Known Issues and Limitations

1. **WebRTC in Safari**: Some emotion detection features may have limited support
2. **WebGL Performance**: 3D visualizations may perform poorly on older hardware
3. **Memory Usage**: Large datasets may require pagination or virtualization

## Future Enhancements

- Progressive Web App (PWA) support
- Offline mode capabilities
- Voice command integration
- Advanced AR/VR visualization features
