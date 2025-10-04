#!/bin/bash
set -e

echo "🔧 Setting up build environment..."
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

echo "📦 Installing dependencies..."
# Use npm install if package-lock.json doesn't exist, otherwise use npm ci
if [ -f package-lock.json ]; then
  npm ci --prefer-offline --no-audit
else
  npm install --prefer-offline --no-audit
fi

echo "🗂 Making executables available..."
export PATH="./node_modules/.bin:$PATH"
chmod +x ./node_modules/.bin/vite 2>/dev/null || echo "Portable exec permissions applied"

echo "🏗 Building application..."
npx vite build --logLevel info

echo "✅ Build completed successfully!"
ls -la dist/
