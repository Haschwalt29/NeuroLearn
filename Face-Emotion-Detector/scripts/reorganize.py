#!/usr/bin/env python3
"""
Reorganize the repository into a clean backend/frontend structure.
- Dry run by default: prints planned moves
- Use --apply to actually move files
- Updates imports and start script paths
"""

import argparse
import shutil
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

# Mapping of source -> destination (relative to ROOT)
MOVES = {
    'web_app.py': 'backend/app.py',
    'improved_pretrained_model.py': 'backend/models/emotion_detector.py',
    'realtime_webcam.py': 'backend/scripts/realtime_webcam.py',
    'templates/index.html': 'backend/templates/index.html',
    'templates/realtime.html': 'backend/templates/realtime.html',
    'ai-tutor-frontend/index.html': 'frontend/ai-tutor/index.html',
    'ai-tutor-frontend/demo.html': 'frontend/ai-tutor/demo.html',
    'ai-tutor-frontend/styles.css': 'frontend/ai-tutor/styles.css',
    'ai-tutor-frontend/app.js': 'frontend/ai-tutor/app.js',
    'ai-tutor-frontend/emotion-integration.js': 'frontend/ai-tutor/emotion-integration.js',
    'ai-tutor-frontend/package.json': 'frontend/ai-tutor/package.json',
    'start-ai-tutor.py': 'scripts/start_ai_tutor.py',
    'test-backend.py': 'scripts/test_backend.py',
    'simple_pretrained_demo.py': 'scripts/simple_pretrained_demo.py',
    'happyboy.jpg': 'assets/samples/happyboy.jpg',
    'sadwoman.jpg': 'assets/samples/sadwoman.jpg',
}

DIR_MOVES = {
    'images': 'data/images',
}

def ensure_dirs():
    required = [
        'backend/models', 'backend/scripts', 'backend/templates', 'backend/static',
        'frontend/ai-tutor', 'data/images', 'assets/samples', 'scripts', 'notebooks'
    ]
    for d in required:
        (ROOT / d).mkdir(parents=True, exist_ok=True)

def move_file(src_rel: str, dst_rel: str, apply: bool):
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    if not src.exists():
        return f"SKIP (missing): {src_rel}"
    if not apply:
        return f"MOVE: {src_rel} -> {dst_rel}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return f"✔ moved: {src_rel} -> {dst_rel}"

def move_dir(src_rel: str, dst_rel: str, apply: bool):
    src = ROOT / src_rel
    dst = ROOT / dst_rel
    if not src.exists():
        return f"SKIP (missing dir): {src_rel}"
    if not apply:
        return f"MOVE DIR: {src_rel} -> {dst_rel}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst))
    return f"✔ moved dir: {src_rel} -> {dst_rel}"

def update_imports_in_file(path: Path, replacements: list[tuple[str, str]], apply: bool):
    if not path.exists():
        return None
    content = path.read_text(encoding='utf-8')
    new_content = content
    for old, new in replacements:
        new_content = re.sub(old, new, new_content)
    if new_content != content:
        if apply:
            path.write_text(new_content, encoding='utf-8')
            return f"✔ updated imports/paths in {path.relative_to(ROOT)}"
        else:
            return f"UPDATE: {path.relative_to(ROOT)} (imports/paths)"
    return None

def update_paths(apply: bool):
    changes = []
    # web_app.py -> backend/app.py updates
    app_py = ROOT / 'backend/app.py'
    changes.append(update_imports_in_file(
        app_py,
        [
            (r"from improved_pretrained_model import EmotionDetector", r"from models.emotion_detector import EmotionDetector"),
        ],
        apply
    ))
    # start script paths
    start_script = ROOT / 'scripts/start_ai_tutor.py'
    changes.append(update_imports_in_file(
        start_script,
        [
            (r"\bweb_app.py\b", r"backend/app.py"),
            (r"ai-tutor-frontend", r"frontend/ai-tutor"),
        ],
        apply
    ))
    return [c for c in changes if c]

def main():
    parser = argparse.ArgumentParser(description='Reorganize project structure')
    parser.add_argument('--apply', action='store_true', help='Apply changes (otherwise dry-run)')
    args = parser.parse_args()

    ensure_dirs()

    logs = []
    # Move files
    for src, dst in MOVES.items():
        logs.append(move_file(src, dst, args.apply))
    # Move directories
    for src, dst in DIR_MOVES.items():
        logs.append(move_dir(src, dst, args.apply))

    # Update imports/paths
    logs.extend(update_paths(args.apply))

    print("\nReorganization Plan:" if not args.apply else "\nReorganization Applied:")
    for line in filter(None, logs):
        print("-", line)

    print("\nNext steps:")
    print("- Verify backend runs: python backend/app.py")
    print("- Serve frontend: cd frontend/ai-tutor && python -m http.server 8080")
    print("- Update any remaining hardcoded paths if needed.")

if __name__ == '__main__':
    main()
