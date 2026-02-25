#!/bin/bash

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         🤖 ZALO BOT - START ALL SERVICES                      ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Activate virtual environment
source venv/bin/activate

# Create logs directory
mkdir -p logs

# Start Flask Server
echo -e "${YELLOW}[1/3] Starting Flask Bot Server...${NC}"
python3 zalo_bot.py > logs/flask.log 2>&1 &
FLASK_PID=$!
echo -e "${GREEN}✅ Flask Server started (PID: $FLASK_PID)${NC}"

sleep 2

# Start Auto-Reply
echo -e "${YELLOW}[2/3] Starting Auto-Reply Bot...${NC}"
python3 auto_reply.py > logs/autoreply.log 2>&1 &
AUTOREPLY_PID=$!
echo -e "${GREEN}✅ Auto-Reply started (PID: $AUTOREPLY_PID)${NC}"

sleep 2

# Start Dashboard
echo -e "${YELLOW}[3/3] Starting Dashboard...${NC}"
python3 dashboard.py > logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo -e "${GREEN}✅ Dashboard started (PID: $DASHBOARD_PID)${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}All services started successfully!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Services running:"
echo "  1. Flask Bot Server: http://127.0.0.1:5002"
echo "  2. Auto-Reply Bot: Processing messages"
echo "  3. Dashboard: http://localhost:5003"
echo ""
echo "Logs:"
echo "  - Flask: logs/flask.log"
echo "  - Auto-Reply: logs/autoreply.log"
echo "  - Dashboard: logs/dashboard.log"
echo ""
echo "Stop all services:"
echo "  kill $FLASK_PID $AUTOREPLY_PID $DASHBOARD_PID"
echo ""
echo "Or press Ctrl+C to stop"
echo ""

# Wait for all processes
wait
