# Target Project Structure

This repository will be organized into a standard backend/frontend layout with scripts, data, and docs.

```
Face-Emotion-Detector/
├── backend/
│   ├── app.py                    # Flask app (moved from web_app.py)
│   ├── models/
│   │   └── emotion_detector.py   # EmotionDetector (from improved_pretrained_model.py)
│   ├── scripts/
│   │   └── realtime_webcam.py    # Realtime webcam runner (from root)
│   ├── templates/                # Jinja templates (moved from /templates)
│   │   ├── index.html
│   │   └── realtime.html
│   └── static/                   # (optional) static assets
│
├── frontend/
│   └── ai-tutor/                 # UI (from ai-tutor-frontend/)
│       ├── index.html
│       ├── demo.html
│       ├── styles.css
│       ├── app.js
│       ├── emotion-integration.js
│       └── package.json
│
├── data/
│   └── images/                   # datasets (moved from /images)
│       ├── train/
│       └── test/
│
├── assets/
│   └── samples/                  # sample images, media (happyboy.jpg, sadwoman.jpg)
│
├── notebooks/
│   ├── Untitled.ipynb
│   └── Untitled1.ipynb
│
├── scripts/
│   ├── start_ai_tutor.py         # start script (from start-ai-tutor.py)
│   ├── test_backend.py           # backend tests (from test-backend.py)
│   └── simple_pretrained_demo.py # demo (from root)
│
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── TROUBLESHOOTING.md
└── PROJECT_STRUCTURE.md (this file)
```

Notes
- Flask will run from `backend/app.py` with `template_folder="templates"` and `static_folder="static"` (both relative to backend/).
- Imports will change to `from models.emotion_detector import EmotionDetector`.
- Start script will launch backend from the new path and serve frontend from `frontend/ai-tutor`.
