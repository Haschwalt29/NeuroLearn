#!/bin/bash
set -e

echo "🔧 Setting up build environment..."
echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

echo "📦 Installing dependencies..."
npm ci --prefer-offline --no-audit

echo "🗂 Making executables available..."
export PATH="./node_modules/.bin:$PATH"
chmod +x ./node_modules/.bin/vite || true

echo "🏗 Building application..."
npx vite build --logLevel info

echo "✅ Build completed successfully!"
ls -la dist/
