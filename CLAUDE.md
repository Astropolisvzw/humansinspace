# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a MicroPython project for Raspberry Pi Pico W that displays the current number of humans in space on a Waveshare 2.9" e-Paper display. It queries the Open Notify API (http://api.open-notify.org/astros.json) to fetch real-time astronaut data and displays it with multi-language headers (Dutch, English, French).

## Hardware Configuration

- **Target Device**: Raspberry Pi Pico W running MicroPython
- **Display**: Waveshare 2.9" e-Paper Display (128x296 pixels, monochrome)
- **Pin Configuration** (defined in epaper.py and his.py):
  - RST_PIN = 12 (Reset)
  - DC_PIN = 8 (Data/Command)
  - CS_PIN = 9 (Chip Select)
  - BUSY_PIN = 13 (Busy status)
  - SPI Bus 1 at 4MHz baudrate

## Project Structure

- `sync/` - Directory containing code that syncs to the Pico (configured via .vscode/settings.json)
  - `humansinspace.py` - Full application combining e-paper display, API query, and formatted output
  - `epaper.py` - Waveshare 2.9" e-Paper display driver (EPD_2IN9_D class)
  - `wifi.py` - WiFi connection setup using credentials from secrets.py
  - `urequests.py` - MicroPython HTTP request library
  - `secrets.py` - WiFi credentials (SSID and PASSWORD)
  - `Pico_ePaper-2.9-C.py` - Alternative e-paper driver for different display variant
- `his.py` - Root-level entry point script (appears to be older version)
- `Pico_ePaper_Code/` - Vendor-provided example code and drivers from Waveshare (reference only)

## Development Setup

This project uses the MicroPico VS Code extension for development and deployment to the Pico.

**Recommended VS Code Extensions**:
- paulober.pico-w-go (MicroPico)
- ms-python.python
- ms-python.vscode-pylance
- visualstudioexptteam.vscodeintellicode

**MicroPico Configuration** (in .vscode/settings.json):
- Sync folder: `sync/` - Only files in this directory are uploaded to the Pico
- Auto-opens on start

## Working with the Code

### Testing Locally
MicroPython imports like `machine`, `framebuf`, `utime`, `urequests`, and `ujson` won't resolve on desktop Python. The .vscode/settings.json includes Pico-W stubs for autocomplete but code must be deployed to the Pico to run.

### Deploying to Pico
1. Connect Pico W via USB
2. Use MicroPico extension commands to upload files from `sync/` directory
3. Run `humansinspace.py` from the Pico's REPL or set as main.py

### WiFi Configuration
Edit `sync/secrets.py` with your network credentials before deploying. This file contains plain-text credentials and should not be committed to public repositories.

## Key Architecture Concepts

### E-Paper Display Driver (EPD_2IN9_D)
The `EPD_2IN9_D` class in both epaper.py and his.py extends `framebuf.FrameBuffer`, providing:
- Low-level SPI communication with the display
- LUT (Look-Up Table) management for full and partial updates
- Full update mode (complete screen refresh)
- Partial update mode (faster updates, available in epaper.py only)
- Custom helper methods:
  - `draw_large_number()` - Creates bold numbers via overlapping text
  - `center_text()` - Horizontally centers text strings

The display uses a monochrome 1-bit framebuffer (MONO_HLSB format) where 0x00 = black, 0xff = white.

### Display Update Flow
1. Initialize display with `EPD_2IN9_D()`
2. Clear screen with `Clear(0x00)`
3. Fill framebuffer with `fill(0xff)` for white background
4. Draw content using `text()`, `draw_large_number()`, `pixel()` methods
5. Send buffer to display with `display(epd.buffer)`
6. Put display to sleep with `sleep()` to conserve power

### API Integration
The Open Notify API returns JSON with:
- `number` - total count of humans in space
- `people` - array of objects with `name` and `craft` fields

The humansinspace.py implementation displays up to 8 astronauts with truncated names if they exceed 15 characters.

## Common Operations

### Run the main application
Upload and execute `sync/humansinspace.py` on the Pico via MicroPico extension.

### Test e-paper display only
Upload and run `sync/epaper.py` which has a test pattern in its `__main__` block.

### Test API connection
Upload and run `sync/humansinspace.py` (the minimal version) to test API connectivity without display.

## Important Notes

- E-paper displays have slow refresh rates (2-5 seconds). Full updates clear the screen completely to prevent ghosting.
- The display retains its image when powered off (bistable display technology).
- WiFi credentials in secrets.py are stored in plaintext - secure appropriately.
- The urequests library is a lightweight HTTP client for MicroPython with a subset of the requests API.
- Always call `sleep()` on the display after updates to reduce power consumption.
