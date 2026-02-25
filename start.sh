#!/bin/bash

echo "🚀 Starting Zalo Bot Services..."
echo "================================"

# Kiểm tra Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed!"
    exit 1
fi

# Tắt services cũ
echo "🛑 Stopping old services..."
docker-compose down -v 2>/dev/null || true

# Build images
echo "🔨 Building Docker images..."
docker-compose build

# Start services
echo "🚀 Starting services..."
docker-compose up -d

# Chờ services khởi động
echo "⏳ Waiting for services to start..."
sleep 5

# Kiểm tra health
echo "🏥 Checking health..."
echo ""

echo "✅ Flask Server (5001):"
curl -s http://localhost:5001/health | python -m json.tool || echo "❌ Not running"

echo ""
echo "✅ Zalo Bot (5002):"
curl -s http://localhost:5002/health | python -m json.tool || echo "❌ Not running"

echo ""
echo "✅ Dashboard (5004):"
curl -s http://localhost:5004/api/health | python -m json.tool || echo "❌ Not running"

echo ""
echo "================================"
echo "🎉 All services started!"
echo "================================"
echo ""
echo "📊 Dashboard: http://localhost:5004"
echo "🔌 Flask Server: http://localhost:5001/health"
echo "🤖 Zalo Bot: http://localhost:5002/health"
echo ""
