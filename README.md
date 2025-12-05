# Bad Apple on LCD1602 via WiFi Streaming

Stream videos to a Raspberry Pi Pico W connected to an LCD1602 display over WiFi. Originally created to run the iconic "Bad Apple!!" animation, but works with any video.

## Why This Exists

Because running Bad Apple on increasingly ridiculous hardware is a time-honored tradition in the tech community. This implementation streams video over WiFi to avoid the USB serial buffer limitations we encountered (RIP frame 36, you will not be missed 🪦).

## Hardware Requirements

- **Raspberry Pi Pico W** (the W is important - need that WiFi!)
- **LCD1602 display** with I2C backpack
- **4 jumper wires** for I2C connection

### Wiring
```
LCD1602 (I2C) -> Pico W
VCC           -> 3.3V or 5V (check your LCD module)
GND           -> GND
SDA           -> GP10 (Pin 14)
SCL           -> GP11 (Pin 15)
```

## Software Requirements

### For Pico W
- MicroPython firmware
- `pico_i2c_lcd` library ([get it here](https://github.com/T-622/RPI-PICO-I2C-LCD))

### For PC
- Python 3.7+
- OpenCV (`pip install opencv-python`)
- yt-dlp (`pip install yt-dlp`)
- ffmpeg (must be in PATH)

## Setup

### 1. Prepare Your Pico W

1. Flash MicroPython to your Pico W
2. Install the `pico_i2c_lcd` library to the Pico
3. Edit `pico_receiver.py`:
```python
   SSID = "YOUR_WIFI_SSID"
   PASSWORD = "YOUR_WIFI_PASSWORD"
```
4. Upload `pico_receiver.py` to your Pico W as `main.py`
5. Connect your LCD1602 according to the wiring diagram
6. Power on the Pico - it will display its IP address on the LCD

### 2. Encode Your Video

Run the encoder script to download and convert Bad Apple (or any video):
```bash
python prepare_bad_apple.py
```

This will:
- Download the video from YouTube
- Resize it to 20×16 pixels (yes, really)
- Convert it to a binary format optimized for the LCD
- Output `BA30.BIN`

**To encode a different video:** Edit these lines in `prepare_bad_apple.py`:
```python
VIDEO_URL = "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"
DOWNLOAD_FILE = "your_video_raw.mp4"
PROCESSED_FILE = "your_video.mp4"
OUTPUT_BIN = "YOUR_VIDEO.BIN"
```

### 3. Stream to Your Pico

1. Note the IP address shown on the Pico's LCD
2. Edit `pc_streamer.py`:
```python
   PICO_IP = "192.168.1.XXX"  # Replace with your Pico's IP
   VIDEO_FILE = "BA30.BIN"     # Or your custom .BIN file
   FPS = 12                     # Adjust framerate (12-20 recommended)
```
3. Run the streamer:
```bash
   python pc_streamer.py
```

## Performance Notes

- **Recommended FPS:** 12-15 for smooth playback
- **Maximum tested:** ~20 FPS before buffering issues
- The LCD I2C operations are the bottleneck, not WiFi bandwidth
- Higher FPS will cause frames to buffer in the network stack

## Technical Details

### Video Encoding
Each frame is 20×16 pixels, displayed using 8 custom LCD characters (4 per row). The encoder:
1. Converts video to grayscale
2. Applies binary threshold (black/white only)
3. Splits into 5×8 pixel blocks
4. Packs each column into bytes (column-major format)
5. Outputs 40 bytes per frame (8 chars × 5 bytes)

### Display Format
LCD custom characters are 5×8 pixels each. We use all 8 available custom character slots:
```
Row 1: [Char 0] [Char 1] [Char 2] [Char 3]
Row 2: [Char 4] [Char 5] [Char 6] [Char 7]
```

Total display area: 20×16 pixels

## Troubleshooting

### "WiFi failed!" on LCD
- Double-check SSID and password
- Ensure your WiFi is 2.4GHz (Pico W doesn't support 5GHz)
- Check WiFi signal strength

### Video plays too slow/choppy
- Lower the FPS in `pc_streamer.py`
- Reduce LCD I2C frequency (change `LCD_I2C_FREQ` in `pico_receiver.py`)

### "Could not connect to Pico"
- Verify the IP address is correct
- Make sure both devices are on the same network
- Check firewall settings

### Video continues playing after stopping PC script
- This is normal - frames are buffered in the network stack
- Lower FPS to reduce buffering
- The video will finish playing the buffered frames

## Why Not USB Serial?

Initially attempted USB serial streaming, but MicroPython's stdin has a bug/limitation that causes it to deadlock after ~35-40 consecutive reads. WiFi doesn't have this issue and is actually more convenient anyway.

## Credits

- Original Bad Apple!! animation: ZUN (Touhou Project)
- Video: Nico Nico Douga user "あにら"
- Inspired by the countless "Bad Apple on X" projects across the internet

## License

MIT License - Do whatever you want with it. If you make something cool, let me know!

## Contributing

Found a bug? Have an optimization? PRs welcome! This was a learning project so there's definitely room for improvement.

---

**Fun fact:** This entire project exists because frame 36 refused to cooperate over USB serial. Thanks, frame 36. 👻