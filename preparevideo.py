import cv2
import numpy as np
import subprocess
import os
from yt_dlp import YoutubeDL

# Configuration
VIDEO_URL = "https://www.youtube.com/watch?v=9lNZ_Rnr7Jc"  # Bad Apple video, replace with whatever video you want
DOWNLOAD_FILE = "bad_apple_raw.mp4" # Same here, replace to the whatever you want
PROCESSED_FILE = "bad_apple.mp4"
OUTPUT_BIN = "BA30.BIN" # You have to replace this too if you dont want to overwrite the bad apple bin

# LCD1602 layout - using custom characters for 4x2 display
CHAR_W, CHAR_H = 5, 8  # Character dimensions in pixels
LCD_COLS, LCD_ROWS = 4, 2  # Using 8 custom characters (4 per row)
FRAME_W, FRAME_H = CHAR_W * LCD_COLS, CHAR_H * LCD_ROWS  # 20x16 pixels total

def download_video(url, filename):
    """Download video from YouTube."""
    print("Downloading video...")
    ydl_opts = {
        "format": "mp4[height<=240]",  # Low resolution
        "outtmpl": filename
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def convert_video(input_file, output_file):
    """Convert and resize video using ffmpeg."""
    print("Converting and resizing video...")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-vf", f"scale={FRAME_W}:{FRAME_H}:flags=lanczos",
        output_file
    ], check=True)

def compress_block(block):
    """Compress 5x8 pixel block into 5 bytes (column-major format)."""
    compressed = [0] * 5
    
    for col in range(5):
        val = 0
        for row in range(8):
            # Pack pixels into bits: bit 7 = row 0, bit 6 = row 1, etc.
            if block[row, col] > 0:
                val |= (1 << (7 - row))
        compressed[col] = val
    
    return compressed

def generate_bin(video_file, output_bin):
    """Generate binary file from video frames."""
    print("Generating binary file...")
    cap = cv2.VideoCapture(video_file)
    frames_bin = []
    
    frame_num = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale and threshold to black/white
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, bw = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
        
        frame_data = []
        
        # Process 8 characters (4 top row + 4 bottom row)
        for row_char in range(LCD_ROWS):
            for col_char in range(4):
                # Extract 5x8 pixel block
                y_start = row_char * CHAR_H
                y_end = (row_char + 1) * CHAR_H
                x_start = col_char * CHAR_W
                x_end = (col_char + 1) * CHAR_W
                
                block = bw[y_start:y_end, x_start:x_end]
                
                # Compress and add to frame data
                compressed = compress_block(block)
                frame_data.extend(compressed)
        
        frames_bin.append(frame_data)
        frame_num += 1
    
    cap.release()
    
    # Write all frames to binary file
    with open(output_bin, "wb") as f:
        for frame in frames_bin:
            f.write(bytearray(frame))
    
    print(f"Done! {len(frames_bin)} frames saved to {output_bin}")

def main():
    """Main workflow."""
    if not os.path.exists(DOWNLOAD_FILE):
        download_video(VIDEO_URL, DOWNLOAD_FILE)
    
    convert_video(DOWNLOAD_FILE, PROCESSED_FILE)
    generate_bin(PROCESSED_FILE, OUTPUT_BIN)
    
    print("\nEncoding complete!")
    print(f"Upload '{OUTPUT_BIN}' to your PC and run pc_streamer.py")

if __name__ == "__main__":
    main()