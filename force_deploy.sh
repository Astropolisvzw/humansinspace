#!/bin/bash

# Force deploy by interrupting any running program first
# This script sends Ctrl+C to the Pico to interrupt any running program,
# then uploads all files and starts the program again.

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

MPREMOTE="/Users/mike/.local/bin/mpremote"

# Kill any existing local mpremote processes
echo -e "${YELLOW}Cleaning up any existing processes...${NC}"
pkill -9 -f mpremote 2>/dev/null
sleep 1

echo -e "${GREEN}Force deploying to Pico...${NC}"

# Auto-detect Pico
echo "Detecting Pico..."
PICO_DEVICE=$($MPREMOTE connect list | grep "MicroPython Board" | awk '{print $1}')

if [ -z "$PICO_DEVICE" ]; then
    echo -e "${RED}Error: No Pico detected${NC}"
    echo "Please make sure your Pico W is connected via USB"
    exit 1
fi

echo -e "${GREEN}Found Pico at: $PICO_DEVICE${NC}"

echo -e "${YELLOW}Step 1: Sending interrupt signal (Ctrl+C) to stop any running program...${NC}"

# Send Ctrl+C to interrupt the running program on the Pico
if command -v picocom &> /dev/null; then
    (sleep 0.5; printf '\x03\x03\x03\x04') | picocom -b 115200 -qrx 500 $PICO_DEVICE &
    PID=$!
    sleep 2
    kill $PID 2>/dev/null
    wait $PID 2>/dev/null
else
    echo -e "${YELLOW}picocom not found, skipping interrupt step${NC}"
fi

echo -e "${YELLOW}Step 2: Uploading all files...${NC}"
sleep 1

# Upload all files
echo "Uploading secrets.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/secrets.py :secrets.py || { echo -e "${RED}Failed to upload secrets.py${NC}"; exit 1; }

echo "Uploading urequests.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/urequests.py :urequests.py || { echo -e "${RED}Failed to upload urequests.py${NC}"; exit 1; }

echo "Uploading humansinspace_landscape.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/humansinspace_landscape.py :humansinspace_landscape.py || { echo -e "${RED}Failed to upload humansinspace_landscape.py${NC}"; exit 1; }

echo "Uploading humansinspace_color.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/humansinspace_color.py :humansinspace_color.py || { echo -e "${RED}Failed to upload humansinspace_color.py${NC}"; exit 1; }

echo "Uploading webserver.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/webserver.py :webserver.py || { echo -e "${RED}Failed to upload webserver.py${NC}"; exit 1; }

echo "Uploading ntptime.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/ntptime.py :ntptime.py || { echo -e "${RED}Failed to upload ntptime.py${NC}"; exit 1; }

echo "Uploading config.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/config.py :config.py || { echo -e "${RED}Failed to upload config.py${NC}"; exit 1; }

echo "Uploading main.py..."
$MPREMOTE connect $PICO_DEVICE fs cp src/main.py :main.py || { echo -e "${RED}Failed to upload main.py${NC}"; exit 1; }

echo ""
echo -e "${GREEN}All files uploaded!${NC}"
echo -e "${YELLOW}Running main.py...${NC}\n"
$MPREMOTE connect $PICO_DEVICE exec "import main"

echo ""
echo -e "${GREEN}Force deployment complete!${NC}"
