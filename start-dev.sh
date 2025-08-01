#!/bin/bash

echo "🌅 Starting Seraaj v2 Development Environment..."
echo

echo "📦 Installing dependencies..."
pnpm install
echo

echo "🐘 Starting PostgreSQL database..."
docker-compose up -d postgres
echo

echo "🔧 Setting up environment files..."
cp apps/api/.env.example apps/api/.env 2>/dev/null || true
cp apps/web/.env.local.example apps/web/.env.local 2>/dev/null || true
echo

echo "🚀 Starting development servers..."
echo
echo "📍 Frontend will be available at: http://localhost:3000"
echo "📍 API docs will be available at: http://localhost:8000/v1/docs"
echo

echo "Open two terminal windows and run:"
echo
echo "Terminal 1 - API:"
echo "  cd apps/api"
echo "  pip install -r requirements.txt"
echo "  uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "Terminal 2 - Frontend:"
echo "  cd apps/web"
echo "  pnpm dev"
echo

read -p "Press Enter to continue..."