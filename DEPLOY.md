# Quick Deploy Instructions

## Method 1: Using VS Code MicroPico Extension (Recommended for now)

1. Open VS Code in this project folder
2. Connect your Pico W (the MicroPico extension should auto-detect it)
3. Open the Command Palette (Cmd+Shift+P)
4. Type and select: **"MicroPico: Upload project to Pico"**
5. The extension will sync all files from the `src/` folder to your Pico
6. The Pico will automatically run `main.py` and display the landscape view

## Method 2: Manual mpremote (for automation later)

If mpremote is having issues, you may need to:
1. Hold the BOOTSEL button on the Pico while plugging in USB
2. Flash fresh MicroPython firmware from https://micropython.org/download/rp2-pico-w/
3. Then run: `./deploy.sh`

## What Changed

The new display features:
- **Landscape orientation** (296x128)
- **Large prominent number** in center (using custom 7-segment style digits)
- **Border box** around the center section
- **Left/Right columns** showing spacecraft names with count
- Layout: 60px left | 176px center | 60px right

## Files Deployed

- `main.py` - Auto-runs on boot, connects WiFi and displays
- `humansinspace_landscape.py` - New landscape display code
- `secrets.py` - WiFi credentials
- `urequests.py` - HTTP library for API calls
