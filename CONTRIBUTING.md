# Contributing to NeuroLearn

Thank you for your interest in contributing to NeuroLearn! This document provides guidelines for contributing to the AI-powered learning platform.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Contribution Guidelines](#contribution-guidelines)
- [Style Guide](#style-guide)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

All contributors are expected to follow our Code of Conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Support diversity and inclusion
- Create a welcoming environment for everyone

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 16+
- Git
- PostgreSQL (for development)
- Redis (for caching)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/neurolearn-ml/neurolearn.git
   cd neurolearn
   ```

2. **Install dependencies**
   ```bash
   npm run install:all
   ```

3. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/dashboard/.env.example frontend/dashboard/.env
   ```

4. **Initialize database**
   ```bash
   cd backend
   python -c "from aitutor_backend import create_app, db; app = create_app(); db.create_all()"
   ```

5. **Start development servers**
   ```bash
   npm run dev
   ```

## Development Process

### Git Workflow

We use GitHub Flow for our development process:

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   npm run test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add brief description of changes"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Branch Naming Convention

- `feature/` - New features
- `bugfix/` - Bug fixes
- `hotfix/` - Critical fixes for production
- `refactor/` - Code refactoring
- `docs/` - Documentation updates
- `test/` - Test-related changes

## Contribution Guidelines

### Reporting Issues

When reporting issues, please include:

- **Bug reports**: Steps to reproduce, expected vs actual behavior
- **Feature requests**: Clear description of the desired functionality
- **Performance issues**: Environment details and performance metrics

### Pull Request Guidelines

All pull requests should:

1. **Have a clear title and description**
   - Summarize the changes
   - Reference related issues
   - Include screenshots for UI changes

2. **Pass all tests**
   ```bash
   npm run test
   ```

3. **Follow the coding style**
   - Python: PEP 8 with Black formatting
   - JavaScript: ESLint + Prettier
   - React: Standard React patterns

4. **Include tests**
   - Unit tests for new functionality
   - Integration tests for API changes
   - Update existing tests when modifying code

5. **Update documentation**
   - Update README if needed
   - Add inline code comments
   - Update API documentation for backend changes

## Style Guide

### Python (Backend)

Follow PEP 8 with these additional guidelines:

```python
# File: services/emotion_service.py
class EmotionService:
    """Service for emotion detection and analysis."""
    
    def __init__(self):
        """
        Initialize emotion detection service.
        
        Sets up the ML model and preprocessing pipeline.
        """
        self.model = self._load_model()
        self.preprocessor = self._setup_preprocessor()
    
    def detect_emotion(self, image_data: bytes) -> Dict[str, Any]:
        """
        Detect emotion from image data.
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing emotion detection results
            
        Raises:
            ProcessingError: When image processing fails
        """
        try:
            processed_image = self._preprocess_image(image_data)
            prediction = self.model.predict(processed_image)
            return self._format_results(prediction)
        except Exception as e:
            logger.error(f"Emotion detection failed: {str(e)}")
            raise ProcessingError(f"Detection failed: {str(e)}")
```

### JavaScript/React (Frontend)

Follow ESLint + Prettier configuration:

```javascript
// File: components/EmotionDetector.jsx
import React, { useState, useCallback, useEffect } from 'react';
import { useSocketio } from '../hooks/useSocketio';

/**
 * Emotion detection component with real-time camera processing
 */
const EmotionDetector = ({ onEmotionDetected }) => {
  const [isDetecting, setIsDetecting] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  const { socket } = useSocketio();

  /**
   * Start emotion detection process
   */
  const startDetection = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: true 
      });
      
      setIsDetecting(true);
      socket.emit('start_detection');
    } catch (error) {
      console.error('Camera access denied:', error);
    }
  }, [socket]);

  useEffect(() => {
    if (!socket) return;

    socket.on('emotion_update', (data) => {
      setCurrentEmotion(data.emotion);
      onEmotionDetected(data);
    });

    return () => socket.off('emotion_update');
  }, [socket, onEmotionDetected]);

  return (
    <div className="emotion-detector">
      {/* Component JSX */}
    </div>
  );
};

export default EmotionDetector;
```

## Testing

### Backend Testing

```python
# File: tests/test_emotion_service.py
import pytest
from unittest.mock import Mock, patch
from aitutor_backend.services.emotion_service import EmotionService

class TestEmotionService:
    """Test suite for emotion detection service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = EmotionService()
    
    @patch('aitutor_backend.services.emotion_service.load_model')
    def test_detect_emotion_success(self, mock_model):
        """Test successful emotion detection."""
        # Arrange
        mock_model.return_value.predict.return_value = [0.8]
        
        # Act
        result = self.service.detect_emotion(b'fake_image_data')
        
        # Assert
        assert result['confidence'] > 0.5
        assert 'emotion' in result
    
    def test_detect_emotion_invalid_data(self):
        """Test emotion detection with invalid input."""
        with pytest.raises(ProcessingError):
            self.service.detect_emotion(b'')
```

### Frontend Testing

```javascript
// File: tests/components/EmotionDetector.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { EmotionDetector } from '../EmotionDetector';

describe('EmotionDetector', () => {
  const mockOnEmotionDetected = jest.fn();

  beforeEach(() => {
    mockOnEmotionDetected.mockClear();
  });

  it('should render emotion detection interface', () => {
    render(<EmotionDetector onEmotionDetected={mockOnEmotionDetected} />);
    
    expect(screen.getByText('Emotion Detector')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Start Detection' }))
      .toBeInTheDocument();
  });

  it('should handle camera access gracefully', async () => {
    // Mock camera access rejection
    navigator.mediaDevices.getUserMedia.mockRejectedValueOnce(
      new Error('Camera access denied')
    );

    render(<EmotionDetector onEmotionDetected={mockOnEmotionDetected} />);
    
    const startButton = screen.getByRole('button', { name: 'Start Detection' });
    fireEvent.click(startButton);
    
    // Should not crash and handle error gracefully
    await screen.findByText(/unable to access camera/i);
  });
});
```

## Documentation

### Code Documentation

- **Docstrings**: Required for all functions and classes
- **Type hints**: Encourage Python type hints and JSDoc in JavaScript
- **Comments**: Explain complex logic and business rules
- **README**: Keep updated with setup instructions and features

### API Documentation

Update API documentation in `documentation/api.md` when:

- Adding new endpoints
- Modifying existing endpoint behavior
- Changing request/response schemas
- Adding authentication requirements

## Review Process

### Pull Request Review

All PRs require review from at least one maintainer:

1. **Automated checks** must pass
   - Tests must be green
   - Code coverage must not decrease
   - Linting must pass

2. **Human review** focuses on:
   - Code quality and readability
   - Architecture and design decisions
   - Security considerations
   - Performance implications

3. **Approval criteria**:
   - Code follows style guide
   - Tests are comprehensive
   - Documentation is updated
   - No breaking changes without discussion

### Merge Process

Once approved:
1. Squash and merge commits
2. Delete feature branch
3. Update version tags if needed
4. Deploy to staging environment

## Support

### Getting Help

- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Discord**: Active developer community (link in README)
- **Wiki**: Check project wiki for FAQ and guides

### Mentorship

We encourage participation from developers of all skill levels:

- **Good first issues**: Labeled for newcomers
- **Mentor assignment**: Available for complex changes
- **Feedback loops**: Regular check-ins for longer contributions

## Recognition

Contributors will be recognized through:

- **Contributors section** in README
- **Developer spotlight** in releases
- **Annual contributor awards**

Thank you for contributing to NeuroLearn! Together, we're building the future of AI-powered education.
