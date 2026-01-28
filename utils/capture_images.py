#!/usr/bin/env python
"""capture_images.py: Capture images from Raspberry Pi camera.
Usage: capture_images.py --output <output_folder> --count <number_of_images>
"""
import argparse
import os
import time
from picamera2 import Picamera2
from libcamera import controls
import cv2

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Capture images from Raspberry Pi camera.")
    parser.add_argument(
        "--output",
        type=str,
        default="./captured_images",
        help="Output folder for captured images (default: ./captured_images)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of images to capture (default: 10)"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Delay between captures in seconds (default: 2.0)"
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Initialize camera
    picam2 = Picamera2()
    
    # Configure camera with 1920x1080 resolution and a lower-res preview stream
    config = picam2.create_still_configuration(
        main={"size": (1920, 1080)},
        lores={"size": (640, 480)},
        display="lores"
    )
    picam2.configure(config)
    
    # Start camera
    picam2.start()
    
    # Try to set autofocus controls if the camera supports them
    # Note: OV5647 (Pi Camera v1) and similar fixed-focus cameras don't support these controls
    camera_controls = picam2.camera_controls
    if 'AfMode' in camera_controls:
        print("Camera supports autofocus - setting to manual mode with 30cm focus")
        picam2.set_controls({
            "AfMode": controls.AfModeEnum.Manual,
            "LensPosition": 3.0  # Lens position in diopters (1/distance in meters), 3.0 ≈ 0.33m
        })
    else:
        print("Camera has fixed focus (autofocus not supported)")
    
    # Allow camera to warm up
    print("Warming up camera...")
    time.sleep(2)
    
    print(f"Capturing {args.count} images to {args.output}")
    print(f"Resolution: 1920x1080")
    print(f"Delay between captures: {args.delay}s")
    print(f"Press 'q' in preview window to quit early")
    print()
    
    # Create preview window
    cv2.namedWindow("Camera Preview", cv2.WINDOW_NORMAL)
    
    # Capture images
    for i in range(args.count):
        filename = os.path.join(args.output, f"image_{i+1:03d}.jpg")
        print(f"Capturing image {i+1}/{args.count}: {filename}")
        picam2.capture_file(filename)
        
        if i < args.count - 1:  # Don't sleep after the last image
            # Show live preview during delay
            print(f"Preview active for {args.delay}s - adjust objects as needed...")
            start_time = time.time()
            while time.time() - start_time < args.delay:
                # Capture a preview frame
                frame = picam2.capture_array("lores")
                
                # Convert from RGB to BGR for OpenCV display
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                
                # Display countdown on frame
                remaining = args.delay - (time.time() - start_time)
                cv2.putText(frame_bgr, f"Next capture in: {remaining:.1f}s", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                cv2.imshow("Camera Preview", frame_bgr)
                
                # Check for 'q' key to quit early
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nQuitting early...")
                    picam2.stop()
                    cv2.destroyAllWindows()
                    return
    
    # Clean up
    cv2.destroyAllWindows()
    
    # Stop camera
    picam2.stop()
    print(f"\nDone! Captured {args.count} images to {args.output}")

if __name__ == "__main__":
    main()
