# Version 1.8
# with newly added feature for notification and WebSocket integration
import cv2
import numpy as np
import time
import os
from datetime import datetime
from ultralytics import YOLO
import threading
import pyaudio
from queue import Queue
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import json
import asyncio
import websockets
import base64
import plyer  # For desktop notifications

# building the class for detection methods
class DetectionMethod:
    """Base class for detection methods"""
    def __init__(self, name, color=(0, 255, 0), icon="⬤"):
        self.name = name
        self.color = color
        self.enabled = True
        self.icon = icon  # Unicode icon to represent this detection method

    def detect(self, frame):
        """
        Perform detection on a frame
        
        Args:
            frame: Input video frame
            
        Returns:
            detections: List of detection results
            annotated_frame: Frame with annotations
        """
        raise NotImplementedError("Subclasses must implement detect()")
    
    def get_status_text(self, detections):
        """Get status text for display"""
        # Format with icon and count
        count = len(detections)
        if count > 0:
            return f"{self.name}: {count}"
        return f"{self.name}: None"
        
    def draw_fancy_box(self, frame, x, y, w, h, label=None, thickness=2):
        """Draw a fancy bounding box with corner brackets"""
        color = self.color
        
        # Calculate corner length (20% of width/height but at least 10px)
        corner_length = max(min(int(min(w, h) * 0.2), 30), 10)
        
        # Draw corner brackets instead of full rectangle
        # Top-left
        cv2.line(frame, (x, y), (x + corner_length, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_length), color, thickness)
        
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - corner_length, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_length), color, thickness)
        
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + corner_length, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_length), color, thickness)
        
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - corner_length, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_length), color, thickness)
        
        # Draw label with background if provided
        if label:
            # Get text size
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Draw background rectangle
            cv2.rectangle(
                frame, 
                (x, y - text_size[1] - 5), 
                (x + text_size[0] + 5, y), 
                color, 
                -1
            )
            
            # Draw text
            cv2.putText(
                frame,
                label,
                (x + 3, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

# building for motion detection method:
class MotionDetection(DetectionMethod):
    """Motion detection using background subtraction"""
    def __init__(self, threshold=1000, color=(0, 255, 0)):
        super().__init__("Motion", color, icon="🔄")
        self.threshold = threshold
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=16, detectShadows=True
        )
    
    def detect(self, frame):
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(frame)
        
        # Threshold the mask and apply morphological operations
        _, thresh = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((5, 5), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detections = []
        annotated_frame = frame.copy()
        
        # Draw rectangles around motion areas
        for contour in contours:
            if cv2.contourArea(contour) < self.threshold:
                continue
                
            (x, y, w, h) = cv2.boundingRect(contour)
            detections.append({
                "class": "motion",
                "confidence": 1.0,
                "box": [x, y, w, h]
            })
            
            # Draw fancy motion box with pulsing effect
            # Use time to create a pulsing effect on the line thickness
            pulse = 1 + int(abs(np.sin(time.time() * 3)) * 2)
            
            # Draw the fancy box
            self.draw_fancy_box(annotated_frame, x, y, w, h, "Motion", pulse)
            
            # Add motion flow visualization (simplified)
            center_x, center_y = x + w//2, y + h//2
            radius = min(w, h) // 4
            thickness = 1
            
            # Draw radar-like concentric circles
            for r in range(radius, radius*3, radius):
                alpha = int(255 * (1 - r/(radius*3)))
                if alpha > 0:
                    overlay = annotated_frame.copy()
                    cv2.circle(overlay, (center_x, center_y), r, 
                              (*self.color, alpha), thickness)
                    cv2.addWeighted(overlay, 0.5, annotated_frame, 0.5, 0, annotated_frame)
        
        return detections, annotated_frame
    
    def get_status_text(self, detections):
        return f"Motion: {'Detected' if detections else 'None'}"

# YOLO detection method class:
class YOLODetection(DetectionMethod):
    """Object detection using YOLO models"""
    def __init__(self, model_path="yolov10n.pt", confidence=0.5, color=(0, 255, 255)):
        model_name = os.path.basename(model_path).split('.')[0]
        super().__init__(f"YOLO-{model_name}", color, icon="🔍")
        self.model_path = model_path
        self.confidence = confidence
        self.object_detector = YOLO(model_path)
        
        # Color palette for different classes
        self.color_palette = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (255, 192, 203) # Pink
        ]
    
    def get_class_color(self, class_id):
        """Get a consistent color for a class ID"""
        return self.color_palette[class_id % len(self.color_palette)]
    
    def detect(self, frame):
        # Run YOLO inference on the frame
        results = self.object_detector(frame, conf=self.confidence)
        
        detections = []
        annotated_frame = frame.copy()
        
        # Process the results
        if results and len(results) > 0:
            result = results[0]
            
            # Extract detections
            for box in result.boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x, y, w, h = int(x1), int(y1), int(x2 - x1), int(y2 - y1)
                
                # Get confidence
                confidence = float(box.conf[0])
                
                # Get class ID and name
                class_id = int(box.cls[0])
                class_name = result.names[class_id]
                
                # Get color for this class
                class_color = self.get_class_color(class_id)
                
                # Store detection info
                detections.append({
                    "class": class_name,
                    "confidence": confidence,
                    "box": [x, y, w, h],
                    "class_id": class_id
                })
                
                # Create label with emoji icons for common objects
                icon = "📦" # Default box icon
                if class_name == "person":
                    icon = "👤"
                elif class_name == "car" or class_name == "truck":
                    icon = "🚗"
                elif class_name == "dog":
                    icon = "🐕"
                elif class_name == "cat":
                    icon = "🐈"
                elif class_name == "bird":
                    icon = "🐦"
                
                label = f"{icon} {class_name}: {confidence:.2f}"
                
                # Draw fancy bounding box with class-specific color
                self.draw_fancy_box(annotated_frame, x, y, w, h, label)
                
                # Add decoration based on object type
                if class_name == "person":
                    # Add head indicator
                    head_y = y + int(h * 0.2)
                    head_size = int(min(w, h) * 0.15)
                    cv2.circle(annotated_frame, (x + w//2, head_y), head_size, class_color, 1)
                
                # Draw confidence meter
                meter_width = 40
                meter_height = 4
                meter_x = x + w - meter_width - 5
                meter_y = y + h + 15
                
                # Background
                cv2.rectangle(annotated_frame, 
                             (meter_x, meter_y), 
                             (meter_x + meter_width, meter_y + meter_height), 
                             (100, 100, 100), -1)
                
                # Filled portion based on confidence
                filled_width = int(meter_width * confidence)
                cv2.rectangle(annotated_frame, 
                             (meter_x, meter_y), 
                             (meter_x + filled_width, meter_y + meter_height), 
                             class_color, -1)
        
        return detections, annotated_frame

# building the detection mode for person datection mode:
class PersonDetection(YOLODetection):
    """Specialized detection for people only"""
    def __init__(self, model_path="yolov10n.pt", confidence=0.5, color=(255, 0, 0)):
        super().__init__(model_path, confidence, color)
        self.name = "Person"
        self.icon = "👤"
        self.person_count = 0
        self.last_count_update = time.time()
    
    def detect(self, frame):
        detections, _ = super().detect(frame)
        
        # Filter for only person detections
        person_detections = [d for d in detections if d["class"] == "person"]
        
        # Update person counter with smoothing
        current_time = time.time()
        if current_time - self.last_count_update > 1.0:  # Update count every second
            self.person_count = len(person_detections)
            self.last_count_update = current_time
        
        # Clear and create new annotated frame
        annotated_frame = frame.copy()
        
        # Add person counter in corner
        if self.person_count > 0:
            counter_text = f"👤 {self.person_count}"
            cv2.putText(
                annotated_frame,
                counter_text,
                (annotated_frame.shape[1] - 80, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
            )
        
        # Draw detailed person detections
        for detection in person_detections:
            x, y, w, h = detection["box"]
            confidence = detection["confidence"]
            
            # Create label with person ID number
            person_id = person_detections.index(detection) + 1
            label = f"👤 Person #{person_id}: {confidence:.2f}"
            
            # Draw fancy box
            self.draw_fancy_box(annotated_frame, x, y, w, h, label)
            
            # Draw skeleton outline (simplified)
            # Head
            head_y = y + int(h * 0.15)
            head_size = int(min(w, h) * 0.15)
            cv2.circle(annotated_frame, (x + w//2, head_y), head_size, self.color, 2)
            
            # Body
            body_top_y = head_y + head_size
            body_bottom_y = y + int(h * 0.7)
            cv2.line(annotated_frame, (x + w//2, body_top_y), (x + w//2, body_bottom_y), self.color, 2)
            
            # Arms
            arm_y = y + int(h * 0.3)
            cv2.line(annotated_frame, (x + w//2, arm_y), (x + int(w * 0.25), y + int(h * 0.45)), self.color, 2)  # Left arm
            cv2.line(annotated_frame, (x + w//2, arm_y), (x + int(w * 0.75), y + int(h * 0.45)), self.color, 2)  # Right arm
            
            # Legs
            cv2.line(annotated_frame, (x + w//2, body_bottom_y), (x + int(w * 0.35), y + h), self.color, 2)  # Left leg
            cv2.line(annotated_frame, (x + w//2, body_bottom_y), (x + int(w * 0.65), y + h), self.color, 2)  # Right leg
            
            # Draw trail (would need tracking in real implementation)
            # Here we just simulate with random points
            np.random.seed(person_id)  # Make trail consistent for same person ID
            trail_points = []
            for i in range(5):
                offset_x = np.random.randint(-30, 30)
                offset_y = np.random.randint(-30, 30)
                trail_points.append((x + w//2 + offset_x, y + h + offset_y))
            
            # Draw trail with fading effect
            for i in range(len(trail_points)-1):
                alpha = 0.7 - (i * 0.15)  # Fade out
                thickness = 3 - i
                if thickness > 0 and alpha > 0:
                    cv2.line(annotated_frame, trail_points[i], trail_points[i+1], 
                            (int(self.color[0] * alpha), int(self.color[1] * alpha), int(self.color[2] * alpha)), 
                            thickness)
        
        return person_detections, annotated_frame
        
    def get_status_text(self, detections):
        """Override status text to include person counter"""
        count = len(detections)
        if count > 0:
            return f"👤 Person: {count}"
        return f"👤 Person: None"

# Building face detection method:
class NoiseDetection(DetectionMethod):
    """Audio noise detection using microphone input"""
    def __init__(self, threshold=0.1, color=(255, 105, 180)):  # Hot pink color
        super().__init__("Noise", color, icon="🔊")
        self.threshold = threshold
        self.energy_history = []
        self.max_history_size = 100
        self.current_energy = 0
        self.audio_thread = None
        self.stop_audio = False
        self.noise_detected = False
        self.detection_time = None
        self.cooldown_period = 3  # Seconds that noise detection remains shown after detection
        
        # Audio parameters
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.audio = pyaudio.PyAudio()
        
        # Initialize audio processing thread
        self.audio_thread = threading.Thread(target=self._process_audio)
        self.audio_thread.daemon = True
        self.audio_thread.start()
    
    def _process_audio(self):
        """Process audio stream in a separate thread"""
        try:
            stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            while not self.stop_audio:
                # Read audio chunk
                data = stream.read(self.chunk, exception_on_overflow=False)
                
                # Convert to numpy array
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate RMS energy
                energy = np.sqrt(np.mean(np.square(audio_data))) / 32768.0  # Normalize to [0,1]
                
                # Update current energy and history
                self.current_energy = energy
                self.energy_history.append(energy)
                if len(self.energy_history) > self.max_history_size:
                    self.energy_history.pop(0)
                
                # Check for noise detection (spike in energy)
                if energy > self.threshold:
                    self.noise_detected = True
                    self.detection_time = time.time()
                
                # Check if we should reset detection after cooldown
                if self.noise_detected and self.detection_time and time.time() - self.detection_time > self.cooldown_period:
                    self.noise_detected = False
                
                time.sleep(0.01)  # Small sleep to reduce CPU usage
                
        except Exception as e:
            print(f"Audio processing error: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
    
    def detect(self, frame):
        """Detect noise and annotate the frame"""
        detections = []
        annotated_frame = frame.copy()
        height, width, _ = frame.shape
        
        # If noise is detected, add a detection
        if self.noise_detected:
            detections.append({
                "class": "noise",
                "confidence": self.current_energy,
                "box": [0, 0, width, height]  # Full frame "detection"
            })
            
            # Add visualizations for noise detection
            # Get time since detection for fade effect
            time_since_detection = 0
            if self.detection_time:
                time_since_detection = time.time() - self.detection_time
                
            # Calculate fade factor (1.0 at detection time, decreasing to 0.0 at end of cooldown)
            fade_factor = max(0, 1.0 - (time_since_detection / self.cooldown_period))
            
            # Draw audio waveform visualization
            waveform_height = 50
            waveform_width = 200
            waveform_x = width - waveform_width - 10
            waveform_y = height - waveform_height - 10
            
            # Draw waveform background
            cv2.rectangle(
                annotated_frame,
                (waveform_x, waveform_y),
                (waveform_x + waveform_width, waveform_y + waveform_height),
                (0, 0, 0, int(128 * fade_factor)),
                -1
            )
            
            # Draw waveform
            if self.energy_history:
                points = []
                for i, energy in enumerate(self.energy_history[-waveform_width:]):
                    x = waveform_x + i
                    y = waveform_y + waveform_height - int(energy * waveform_height)
                    points.append((x, y))
                
                # Connect points with lines
                for i in range(1, len(points)):
                    intensity = int(255 * fade_factor)
                    cv2.line(
                        annotated_frame,
                        points[i-1],
                        points[i],
                        (0, intensity, intensity),
                        1
                    )
            
            # Draw noise indicator in the corner
            indicator_size = int(80 * fade_factor)
            indicator_x = 20
            indicator_y = 80
            
            # Pulsing effect based on energy
            pulse_size = int(indicator_size * (0.8 + 0.2 * self.current_energy))
            
            # Draw sound waves icon
            for i in range(1, 4):
                thickness = max(1, int(3 * fade_factor))
                radius = pulse_size // 2 * i // 3
                # Draw arc segments to mimic sound waves
                cv2.ellipse(
                    annotated_frame,
                    (indicator_x, indicator_y),
                    (radius, radius),
                    0, -60, 60,
                    (self.color[0], self.color[1], self.color[2], int(255 * fade_factor)),
                    thickness
                )
            
            # Draw text indicator
            text_y = indicator_y + pulse_size // 2 + 20
            sound_level = "LOW"
            if self.current_energy > 0.3:
                sound_level = "HIGH"
            elif self.current_energy > 0.15:
                sound_level = "MEDIUM"
                
            cv2.putText(
                annotated_frame,
                f"SOUND: {sound_level}",
                (indicator_x - 10, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5 * fade_factor,
                self.color,
                1
            )
            
            # Add timestamp of detection
            if self.detection_time:
                timestamp = time.strftime("%H:%M:%S", time.localtime(self.detection_time))
                cv2.putText(
                    annotated_frame,
                    f"Detected: {timestamp}",
                    (indicator_x - 10, text_y + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4 * fade_factor,
                    self.color,
                    1
                )
        
        return detections, annotated_frame
    
    def get_status_text(self, detections):
        """Get status text for display"""
        if self.noise_detected:
            energy_percent = int(self.current_energy * 100)
            return f"🔊 Noise: {energy_percent}%"
        return f"🔊 Noise: None"
    
    def __del__(self):
        """Clean up resources"""
        self.stop_audio = True
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=1.0)
        self.audio.terminate()

# building the class for detection faces
class FaceDetection(DetectionMethod):
    """Face detection using Haar cascades"""
    def __init__(self, color=(0, 0, 255)):
        super().__init__("Face", color)
        # Load Haar cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect(self, frame):
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30)
        )
        
        detections = []
        annotated_frame = frame.copy()
        
        # Process detections
        for (x, y, w, h) in faces:
            detections.append({
                "class": "face",
                "confidence": 1.0,  # Haar cascade doesn't provide confidence scores
                "box": [x, y, w, h]
            })
            
            # Draw rectangle around face
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), self.color, 2)
            
            # Add label
            cv2.putText(
                annotated_frame,
                "Face",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                self.color,
                2,
            )
        
        return detections, annotated_frame


# Update the MultiSurveillanceSystem class to include the new noise detection
def update_multi_surveillance_system():
    """Add the new noise detection to the surveillance system"""
    # Add to detection_methods dictionary in __init__
    # self.detection_methods["noise"] = NoiseDetection(threshold=0.1)
    
    # Update the start method to include the new option
    print("  5: Noise Detection")
    
    # Handle the new toggle key in run method
    # elif key == ord('5'):
    #     self.toggle_detection_method("noise")

# Building the class for Async detector:
class AsyncDetector:
    """Handles asynchronous detection to improve performance"""
    def __init__(self, detection_method):
        self.detection_method = detection_method
        self.frame = None
        self.results = None
        self.processing = False
        self.thread = None
    
    def process_frame(self, frame):
        """Process a new frame if not currently processing"""
        if not self.processing:
            self.frame = frame.copy()
            self.processing = True
            self.thread = threading.Thread(target=self._process)
            self.thread.daemon = True
            self.thread.start()
    
    def _process(self):
        """Process the frame in a separate thread"""
        if self.frame is not None:
            self.results = self.detection_method.detect(self.frame)
            self.processing = False
    
    def get_results(self):
        """Get the latest detection results"""
        return self.results
    
    def is_ready(self):
        """Check if detector is ready to process a new frame"""
        return not self.processing
    
class MultiSurveillanceSystem:
    def __init__(self, camera_source=0, output_folder="multi_surveillance", speak_callback=None):
        self.speak_callback = speak_callback  # Add callback for Trinity's speak function
    # ... rest of __init__

        self.camera_source = camera_source
        self.output_folder = output_folder
        self.cap = None
        self.websocket_clients = set()  # Track connected WebSocket clients
        self.armed = True  # Add armed state
        self.loop = None  # Asyncio event loop for WebSocket
        self.websocket_server = None  # WebSocket server instance
        self.running = True  # Control flag for broadcast loop

        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Recording variables
        self.is_recording = False
        self.video_writer = None
        self.recording_start_time = None

        # Create detection methods
        self.detection_methods = {
            "motion": MotionDetection(threshold=1000),
            "yolo": YOLODetection(model_path="yolov10n.pt", confidence=0.5),
            "person": PersonDetection(model_path="yolov10n.pt", confidence=0.5),
            "face": FaceDetection(),
            "noise": NoiseDetection(threshold=0.1)
        }

        # Initialize async detectors for each method
        self.async_detectors = {}
        for name, method in self.detection_methods.items():
            self.async_detectors[name] = AsyncDetector(method)

        # Active detection methods
        self.active_methods = ["motion", "yolo"]  # Default active methods

        # Detection results
        self.current_detections = {}

    async def websocket_handler(self, websocket, path):
        """Handle WebSocket connections"""
        self.websocket_clients.add(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'arm':
                        self.armed = data.get('value', False)
                        print(f"System {'armed' if self.armed else 'disarmed'} via WebSocket")
                        # Broadcast arm status to all clients
                        arm_data = {
                            'type': 'status',
                            'armed': self.armed
                        }
                        for client in self.websocket_clients:
                            try:
                                await client.send(json.dumps(arm_data))
                            except:
                                pass
                except json.JSONDecodeError:
                    print("Invalid JSON received from WebSocket client")
        except websockets.exceptions.ConnectionClosed:
            print("WebSocket client disconnected")
        finally:
            self.websocket_clients.remove(websocket)

    async def broadcast_detections(self):
        """Broadcast detection results and frames to all connected clients"""
        while self.running:
            if not self.cap or not self.cap.isOpened():
                await asyncio.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                await asyncio.sleep(0.1)
                continue

            frame = cv2.resize(frame, (1100, 600))  # Resize for consistency

            # Process detections
            for method_name in self.active_methods:
                detector = self.async_detectors[method_name]
                if detector.is_ready():
                    detector.process_frame(frame)

                if detector.get_results() is not None:
                    detections, _ = detector.get_results()
                    self.current_detections[method_name] = detector.get_results()

                    if detections:
                        # Prepare detection data
                        detection_data = {
                            'type': 'detection',
                            'detectionType': method_name.capitalize(),
                            'location': self.detection_methods[method_name].name,
                            'stats': {
                                'today': len(detections),
                                'falsePositives': 0  # Placeholder, update with actual logic
                            },
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        }
                        # Broadcast detection data
                        for client in list(self.websocket_clients):
                            try:
                                await client.send(json.dumps(detection_data))
                            except:
                                self.websocket_clients.discard(client)  # Remove disconnected client

            # Encode and send frame
            try:
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                frame_data = {
                    'type': 'frame',
                    'cameraId': 1,  # Update with actual camera ID for multi-camera support
                    'frame': f'data:image/jpeg;base64,{frame_base64}'
                }
                for client in list(self.websocket_clients):
                    try:
                        await client.send(json.dumps(frame_data))
                    except:
                        self.websocket_clients.discard(client)  # Remove disconnected client
            except Exception as e:
                print(f"Error encoding frame: {e}")

            await asyncio.sleep(0.033)  # ~30 FPS

    def start_websocket_server(self):
        """Start the WebSocket server in a separate thread"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.websocket_server = websockets.serve(self.websocket_handler, "localhost", 8765)
            self.loop.run_until_complete(self.websocket_server)
            self.loop.create_task(self.broadcast_detections())
            try:
                self.loop.run_forever()
            except KeyboardInterrupt:
                self.stop_websocket_server()

        ws_thread = threading.Thread(target=run_loop, daemon=True)
        ws_thread.start()

    def stop_websocket_server(self):
        """Stop the WebSocket server and clean up"""
        self.running = False
        if self.loop:
            tasks = asyncio.all_tasks(self.loop)
            for task in tasks:
                task.cancel()
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
        if self.websocket_server:
            self.websocket_server.close()

    def start(self):
        """Start the surveillance system and connect to the camera"""
        self.cap = cv2.VideoCapture(self.camera_source)
        if not self.cap.isOpened():
            raise ValueError(f"Unable to open camera source {self.camera_source}")

        # Start WebSocket server
        self.start_websocket_server()

        print("Multi-Detection Surveillance System started.")
        print("Press 'q' to quit.")
        print("Press '1-9' to toggle detection methods:")
        print("  1: Motion Detection")
        print("  2: YOLO Object Detection")
        print("  3: Person Detection")
        print("  4: Face Detection")
        print("  5: Noise Detection")
        print("Recording: 'r' to start/stop recording")
        print("Screenshot: 's' to save screenshot")

        return self.cap

    def start_recording(self, frame):
        """Start recording video"""
        if self.is_recording:
            return

        height, width, _ = frame.shape
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_folder, f"recording_{timestamp}.mp4")

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(
            output_path, fourcc, 20.0, (width, height)
        )

        self.is_recording = True
        self.recording_start_time = time.time()
        print(f"Started recording: {output_path}")

    def stop_recording(self):
        """Stop recording video"""
        if not self.is_recording:
            return

        self.video_writer.release()
        self.is_recording = False
        duration = time.time() - self.recording_start_time
        print(f"Recording stopped. Duration: {duration:.2f} seconds")

    def save_screenshot(self, frame):
        """Save a screenshot of the current frame"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_folder, f"screenshot_{timestamp}.jpg")
        cv2.imwrite(output_path, frame)
        print(f"Screenshot saved: {output_path}")

    def toggle_detection_method(self, method_key):
        """Toggle a detection method on/off"""
        if method_key in self.detection_methods:
            if method_key in self.active_methods:
                self.active_methods.remove(method_key)
                print(f"Disabled: {self.detection_methods[method_key].name}")
            else:
                self.active_methods.append(method_key)
                print(f"Enabled: {self.detection_methods[method_key].name}")

    def combine_detections(self, frame, annotated_frames):
        """Combine multiple annotated frames into a single display frame"""
        combined_frame = frame.copy()

        for method_name in self.active_methods:
            if method_name in self.current_detections:
                detections, annotated_frame = self.current_detections[method_name]
                diff = cv2.absdiff(annotated_frame, frame)
                mask = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(mask, 20, 255, cv2.THRESH_BINARY)
                masked_annotations = cv2.bitwise_and(annotated_frame, annotated_frame, mask=mask)
                combined_frame = cv2.add(combined_frame, masked_annotations)

        return combined_frame

    def add_status_overlay(self, frame):
        """Add stylish status information overlay to the frame"""
        overlay_frame = frame.copy()
        height, width, _ = frame.shape

        overlay = overlay_frame.copy()
        cv2.rectangle(overlay, (0, 0), (width, 60), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.7, overlay_frame, 0.3, 0, overlay_frame)

        title_text = "MULTI-DETECTION SURVEILLANCE"
        title_size = cv2.getTextSize(title_text, cv2.FONT_HERSHEY_TRIPLEX, 0.7, 2)[0]
        title_x = (width - title_size[0]) // 2

        cv2.putText(
            overlay_frame,
            title_text,
            (title_x + 2, 22),
            cv2.FONT_HERSHEY_TRIPLEX,
            0.7,
            (0, 0, 0),
            2,
        )
        cv2.putText(
            overlay_frame,
            title_text,
            (title_x, 20),
            cv2.FONT_HERSHEY_TRIPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        x_offset = 10
        for i, method_name in enumerate(self.active_methods):
            if method_name in self.current_detections:
                detections, _ = self.current_detections[method_name]
                method = self.detection_methods[method_name]
                status_text = method.get_status_text(detections)

                indicator_color = method.color
                cv2.rectangle(overlay_frame, (x_offset, 35), (x_offset + 10, 45), indicator_color, -1)
                cv2.rectangle(overlay_frame, (x_offset, 35), (x_offset + 10, 45), (255, 255, 255), 1)

                cv2.putText(
                    overlay_frame,
                    status_text,
                    (x_offset + 15, 44),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    2,
                )
                cv2.putText(
                    overlay_frame,
                    status_text,
                    (x_offset + 14, 43),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    method.color,
                    1,
                )

                text_width = cv2.getTextSize(status_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]
                x_offset += text_width + 35

        if self.is_recording:
            current_time = time.time()
            if int(current_time * 2) % 2 == 0:
                cv2.circle(overlay_frame, (width - 30, 20), 10, (0, 0, 255), -1)
                cv2.circle(overlay_frame, (width - 30, 20), 10, (255, 255, 255), 1)
                cv2.putText(
                    overlay_frame,
                    "REC",
                    (width - 70, 25),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (255, 255, 255),
                    2,
                )

                rec_time = time.time() - self.recording_start_time
                time_text = f"{int(rec_time // 60):02d}:{int(rec_time % 60):02d}"
                cv2.putText(
                    overlay_frame,
                    time_text,
                    (width - 70, 45),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(
            overlay_frame,
            current_datetime,
            (10, height - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
        )

        return overlay_frame

    def run(self):
        """Run the multi-detection surveillance system"""
        if self.cap is None:
            self.start()

        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    print("Failed to read frame")
                    break

                frame = cv2.resize(frame, (1100, 600))
                for method_name in self.active_methods:
                    detector = self.async_detectors[method_name]
                    if detector.is_ready():
                        detector.process_frame(frame)

                    if detector.get_results() is not None:
                        self.current_detections[method_name] = detector.get_results()
                        detections, _ = self.current_detections[method_name]
                        if detections and self.speak_callback:
                            status_text = self.detection_methods[method_name].get_status_text(detections)
                            self.speak_callback(f"Detection alert: {status_text}")

                frame = cv2.resize(frame, (1100, 600))  # Resize for consistency
                for method_name in self.active_methods:
                    detector = self.async_detectors[method_name]
                    if detector.is_ready():
                        detector.process_frame(frame)

                    if detector.get_results() is not None:
                        self.current_detections[method_name] = detector.get_results()

                annotated_frames = {method: self.current_detections.get(method, ([], frame))[1]
                                   for method in self.active_methods}
                display_frame = self.combine_detections(frame, annotated_frames)
                display_frame = self.add_status_overlay(display_frame)

                any_detections = any(len(self.current_detections.get(method, ([], None))[0]) > 0
                                    for method in self.active_methods)
                if any_detections and not self.is_recording:
                    self.start_recording(frame)

                if self.is_recording:
                    self.video_writer.write(frame)

                cv2.imshow("Multi-Detection Surveillance System", display_frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                    break
                elif key == ord('r'):
                    if self.is_recording:
                        self.stop_recording()
                    else:
                        self.start_recording(frame)
                elif key == ord('s'):
                    self.save_screenshot(display_frame)
                elif key == ord('1'):
                    self.toggle_detection_method("motion")
                elif key == ord('2'):
                    self.toggle_detection_method("yolo")
                elif key == ord('3'):
                    self.toggle_detection_method("person")
                elif key == ord('4'):
                    self.toggle_detection_method("face")
                elif key == ord('5'):
                    self.toggle_detection_method("noise")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        self.running = False
        if self.is_recording:
            self.stop_recording()
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
        self.stop_websocket_server()

    def __del__(self):
        """Ensure cleanup when object is destroyed"""
        self.cleanup()

def main():
    """Main function to run the multi-detection surveillance system"""
    try:
        surveillance = MultiSurveillanceSystem(camera_source=0)
        surveillance.run()
    except Exception as e:
        print(f"Error running surveillance system: {e}")
    finally:
        print("Surveillance system shut down")

if __name__ == "__main__":
    main()

