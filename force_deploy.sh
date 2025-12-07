#!/bin/bash

# Force deploy by interrupting any running program first

PORT="/dev/cu.usbserial-0130DA97"
MPREMOTE="/Users/mike/.local/bin/mpremote"

echo "Force deploying to Pico..."
echo "Step 1: Sending interrupt signal (Ctrl+C) to stop any running program..."

# Send Ctrl+C multiple times using printf and picocom
(sleep 0.5; printf '\x03\x03\x03\x04') | picocom -b 115200 -qrx 500 $PORT &
PID=$!
sleep 2
kill $PID 2>/dev/null
wait $PID 2>/dev/null

echo "Step 2: Trying to connect with mpremote..."
sleep 1

# Try to upload files
echo "Uploading secrets.py..."
$MPREMOTE connect $PORT fs cp sync/secrets.py :secrets.py

echo "Uploading urequests.py..."
$MPREMOTE connect $PORT fs cp sync/urequests.py :urequests.py

echo "Uploading humansinspace_landscape.py..."
$MPREMOTE connect $PORT fs cp sync/humansinspace_landscape.py :humansinspace_landscape.py

echo "Uploading main.py..."
$MPREMOTE connect $PORT fs cp sync/main.py :main.py

echo ""
echo "Files uploaded! Running main.py..."
$MPREMOTE connect $PORT run main.py

echo ""
echo "Deployment complete!"
