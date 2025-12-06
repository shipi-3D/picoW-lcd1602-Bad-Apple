import socket
import time

# Configuration - UPDATE THESE
PICO_IP = "192.168.1.XXX"
PORT = 8888
FPS = 30  # This becomes max FPS - actual speed limited by Pico processing
FRAME_SIZE = 40
VIDEO_FILE = "BA30.BIN"

def main():
    print(f"[INFO] Connecting to Pico at {PICO_IP}:{PORT}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PICO_IP, PORT))
            s.settimeout(5)  # 5 second timeout for ACKs
            print("[INFO] Connected! Starting stream...")
            
            frame_number = 0
            start_time = time.time()
            
            with open(VIDEO_FILE, "rb") as f:
                while True:
                    frame = f.read(FRAME_SIZE)
                    if not frame:
                        break
                    
                    # Send frame
                    s.sendall(frame)
                    frame_number += 1
                    
                    # Wait for ACK from Pico
                    try:
                        ack = s.recv(1)
                        if ack != b'A':
                            print(f"[WARN] Unexpected ACK at frame {frame_number}: {ack}")
                    except socket.timeout:
                        print(f"[ERROR] Timeout waiting for ACK at frame {frame_number}")
                        return
                    
                    if frame_number % 100 == 0:
                        elapsed = time.time() - start_time
                        actual_fps = frame_number / elapsed
                        print(f"[INFO] Sent {frame_number} frames (avg {actual_fps:.1f} FPS)...")
                    
                    # Optional: still limit max speed
                    time.sleep(1/FPS)
            
            elapsed = time.time() - start_time
            print(f"[INFO] Streaming complete! {frame_number} frames in {elapsed:.1f}s ({frame_number/elapsed:.1f} FPS)")
            
    except ConnectionRefusedError:
        print(f"[ERROR] Could not connect to {PICO_IP}:{PORT}")
    except FileNotFoundError:
        print(f"[ERROR] Video file '{VIDEO_FILE}' not found")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    main()