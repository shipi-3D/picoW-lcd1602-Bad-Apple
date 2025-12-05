import socket
import time

# Configuration - UPDATE THESE
PICO_IP = "192.168.1.XXX"  # Replace with IP shown on Pico's LCD
PORT = 8888
FPS = 12  # Frames per second (try 12-20, higher may cause buffering)
FRAME_SIZE = 40  # 8 characters × 5 bytes each
VIDEO_FILE = "BA30.BIN"  # Path to your encoded video file

def main():
    print(f"[INFO] Connecting to Pico at {PICO_IP}:{PORT}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PICO_IP, PORT))
            print("[INFO] Connected! Starting stream...")
            
            frame_number = 0
            with open(VIDEO_FILE, "rb") as f:
                while True:
                    frame = f.read(FRAME_SIZE)
                    if not frame:
                        print("[INFO] Reached end of file")
                        break
                    
                    s.sendall(frame)
                    frame_number += 1
                    
                    if frame_number % 100 == 0:
                        print(f"[INFO] Sent {frame_number} frames...")
                    
                    time.sleep(1/FPS)
            
            print(f"[INFO] Streaming complete! Sent {frame_number} frames")
            time.sleep(5)
            
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to {PICO_IP}:{PORT}")
        print("[INFO] Make sure the Pico is running and check the IP address")
    except FileNotFoundError:
        print(f"[ERROR] Video file '{VIDEO_FILE}' not found")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()