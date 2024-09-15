
import cv2
import numpy as np
import time

import math

class ColorTracker:
    def __init__(self, camera_device_id=0, image_width=320, image_height=240):
        self.CAMERA_DEVICE_ID = camera_device_id
        self.IMAGE_WIDTH = image_width
        self.IMAGE_HEIGHT = image_height
        self.hsv_min = np.array((50, 80, 80))
        self.hsv_max = np.array((120, 255, 255))
        self.colors = [(210.0, 0.8, 97.3)]  # Initialize with white color
        self.fps = 0
        self.cap = None
        
    def start(self):
        try:
            # Create video capture
            self.cap = cv2.VideoCapture(self.CAMERA_DEVICE_ID)

            # Set resolution to 320x240 to reduce latency
            self.cap.set(3, self.IMAGE_WIDTH)
            self.cap.set(4, self.IMAGE_HEIGHT)

            while True:
                # Record start time
                start_time = time.time()
                # Read the frames from the camera
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to grab frame")
                    break
                frame = cv2.blur(frame, (3, 3))

                # Convert the image to HSV space and find range of colors
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                cv2.namedWindow('frame')
                cv2.setMouseCallback('frame', self.on_mouse_click, frame)

                # Update HSV thresholds if colors have been sampled
                if self.colors:
                    # Find max & min h, s, v
                    minh = min(c[0] for c in self.colors)
                    mins = min(c[1] for c in self.colors)
                    minv = min(c[2] for c in self.colors)
                    maxh = max(c[0] for c in self.colors)
                    maxs = max(c[1] for c in self.colors)
                    maxv = max(c[2] for c in self.colors)

                    print("New HSV threshold: ", (minh, mins, minv), (maxh, maxs, maxv))
                    self.hsv_min = np.array((minh, mins, minv))
                    self.hsv_max = np.array((maxh, maxs, maxv))

                thresh = cv2.inRange(hsv, self.hsv_min, self.hsv_max)
                thresh2 = thresh.copy()

                # Find contours
                contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

                # Finding contour with maximum area
                max_area = 0
                best_cnt = None
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if area > max_area:
                        max_area = area
                        best_cnt = cnt

                # Finding centroids of best_cnt and draw a circle there
                if best_cnt is not None:
                    M = cv2.moments(best_cnt)
                    cx, cy = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
                    cv2.circle(frame, (cx, cy), 5, 255, -1)
                    print("Central pos: (%d, %d)" % (cx, cy))
                else:
                    print("[Warning]Tag lost...")

                # Show the original and processed image
                # cv2.imshow('frame', self.visualize_fps(frame))
                cv2.imshow('thresh', self.visualize_fps(thresh2))
                
                # Record end time
                end_time = time.time()
                # Calculate FPS
                seconds = end_time - start_time
                self.fps = 1.0 / seconds
                print("Estimated fps:{0:0.1f}".format(self.fps))

                # If key pressed is 'Esc' then exit the loop
                if cv2.waitKey(33) == 27:
                    break
        except Exception as e:
            print(e)
        finally:
            # Clean up and exit the program
            cv2.destroyAllWindows()
            if self.cap:
                self.cap.release()

    def on_mouse_click(self, event, x, y, flags, frame):
        if event == cv2.EVENT_LBUTTONUP:
            color_bgr = frame[y, x]
            color_rgb = tuple(reversed(color_bgr))
            print(color_rgb)

            color_hsv = self.rgb2hsv(color_rgb[0], color_rgb[1], color_rgb[2])
            print(color_hsv)

            self.colors.append(color_hsv)
            print(self.colors)

    def visualize_fps(self, image):
        if len(np.shape(image)) < 3:
            text_color = (255, 255, 255)  # white
        else:
            text_color = (0, 255, 0)  # green
        row_size = 20  # pixels
        left_margin = 24  # pixels

        font_size = 1
        font_thickness = 1

        # Draw the FPS counter
        fps_text = 'FPS = {:.1f}'.format(self.fps)
        text_location = (left_margin, row_size)
        cv2.putText(image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                    font_size, text_color, font_thickness)

        return image

    def hsv2rgb(self, h, s, v):
        h = float(h) * 2
        s = float(s) / 255
        v = float(v) / 255
        h60 = h / 60.0
        h60f = math.floor(h60)
        hi = int(h60f) % 6
        f = h60 - h60f
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        r, g, b = 0, 0, 0
        if hi == 0: r, g, b = v, t, p
        elif hi == 1: r, g, b = q, v, p
        elif hi == 2: r, g, b = p, v, t
        elif hi == 3: r, g, b = p, q, v
        elif hi == 4: r, g, b = t, p, v
        elif hi == 5: r, g, b = v, p, q
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        return (r, g, b)

    def rgb2hsv(self, r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx = max(r, g, b)
        mn = min(r, g, b)
        df = mx - mn
        if mx == mn:
            h = 0
        elif mx == r:
            h = (60 * ((g - b) / df) + 360) % 360
        elif mx == g:
            h = (60 * ((b - r) / df) + 120) % 360
        elif mx == b:
            h = (60 * ((r - g) / df) + 240) % 360
        if mx == 0:
            s = 0
        else:
            s = df / mx
        v = mx

        h = int(h / 2)
        s = int(s * 255)
        v = int(v * 255)

        return (h, s, v)