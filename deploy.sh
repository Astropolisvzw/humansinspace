#!/bin/bash

# Deploy script for Humans in Space Pico project
# This script uploads all necessary files to the Pico W

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Kill any existing mpremote processes to avoid conflicts
echo -e "${YELLOW}Cleaning up any existing processes...${NC}"
pkill -9 -f mpremote 2>/dev/null
sleep 1

echo -e "${GREEN}Deploying Humans in Space to Pico W...${NC}"

# Find mpremote
MPREMOTE="/Users/mike/.local/bin/mpremote"

if [ ! -f "$MPREMOTE" ]; then
    echo -e "${RED}Error: mpremote not found at $MPREMOTE${NC}"
    echo "Please install it with: pipx install mpremote"
    exit 1
fi

# Auto-detect Pico
echo "Detecting Pico..."
PICO_DEVICE=$($MPREMOTE connect list | grep "MicroPython Board" | awk '{print $1}')

if [ -z "$PICO_DEVICE" ]; then
    echo -e "${RED}Error: No Pico detected${NC}"
    echo "Please make sure:"
    echo "1. Your Pico W is connected via USB"
    echo "2. No other programs (like Thonny) are using the serial port"
    exit 1
fi

echo -e "${GREEN}Found Pico at: $PICO_DEVICE${NC}\n"

echo -e "${GREEN}Uploading files...${NC}"

# Upload each file
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

echo -e "\n${GREEN}All files uploaded successfully!${NC}"
echo -e "${YELLOW}Running main.py...${NC}\n"

# Run the main script
$MPREMOTE connect $PICO_DEVICE exec "import main"

echo -e "\n${GREEN}Deployment complete!${NC}"
echo "The Pico will automatically run main.py on next boot."
