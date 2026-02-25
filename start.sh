#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Kill existing processes
echo -e "${YELLOW}🔥 Killing existing processes...${NC}"
pkill -f "flask_server" 2>/dev/null
pkill -f "dashboard" 2>/dev/null
pkill -f "zalo_bot" 2>/dev/null
sleep 2

# Kill by port if still running
lsof -ti:5001 | xargs kill -9 2>/dev/null
lsof -ti:5004 | xargs kill -9 2>/dev/null
sleep 1

echo -e "${GREEN}✅ Old processes killed${NC}\n"

# Start Flask Bot Server
echo "============================================================"
echo -e "${BLUE}🔌 FLASK BOT SERVER${NC}"
echo "============================================================"
echo "Running on http://127.0.0.1:5001"
echo "============================================================"
python flask_server.py &
FLASK_PID=$!
sleep 2

# Start Dashboard
echo ""
echo "============================================================"
echo -e "${BLUE}📊 ZALO BOT DASHBOARD${NC}"
echo "============================================================"
echo "Open http://localhost:5004 in your browser"
echo "============================================================"
python dashboard.py &
DASHBOARD_PID=$!
sleep 2

# Start Zalo Bot Auto-Reply
echo ""
echo "============================================================"
echo -e "${BLUE}🤖 Zalo Bot Auto-Reply Started!${NC}"
echo "============================================================"
echo "Waiting for messages... (Press Ctrl+C to stop)"
echo "============================================================"
python zalo_bot.py &
BOT_PID=$!

echo -e "${GREEN}✅ All services started!${NC}"

# Trap Ctrl+C to kill all background processes
trap "kill $FLASK_PID $DASHBOARD_PID $BOT_PID 2>/dev/null; exit" INT TERM

# Wait for all processes
wait
