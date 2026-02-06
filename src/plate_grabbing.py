from ultralytics import YOLO
import cv2
import serial
import time

# ==========================================
# Tuning Parameters (Critical!)
# ==========================================
COM_PORT = '/dev/ttyUSB0'
BAUD_RATES = 9600
CAMERA_ID = 0

# --- Recognition Filtering (Fix misidentification) ---
# You must know the Class ID of the plate in the model.
# Usually 0 if there is only one class. If using COCO model, 0 is person.
TARGET_CLASS_ID = 0  

# --- Navigation Parameters (Fix distance issues) ---
ALIGN_TOLERANCE = 80   # Tolerance range for left/right alignment (pixels)
MOVE_STEP_TIME  = 0.05 # Shorten movement time for finer adjustments

# --- Distance Locking (Fix fixed arm length issue) ---
# Since the arm extension length is fixed, we force the car to stop at a fixed distance.
# Please measure with a real plate: what is the area when the arm can grab it perfectly?
IDEAL_AREA = 180000      # Assumption: The area at perfect distance is 180,000
AREA_TOLERANCE = 15000   # Allowable error range

# Calculate the "Grab Range"
MIN_GRAB_AREA = IDEAL_AREA - AREA_TOLERANCE
MAX_GRAB_AREA = IDEAL_AREA + AREA_TOLERANCE

# --- Arm Action Timings ---
TIME_EXTEND  = 25.0
TIME_RETRACT = 21.0
TIME_GRAB    = 1.2
TIME_RELEASE = 1.2

# ==========================================
# Initialization
# ==========================================
try:
    ser = serial.Serial(COM_PORT, BAUD_RATES, timeout=1)
    time.sleep(2)
    print(f"Arduino connection successful")
except Exception as e:
    print(f"Arduino connection failed: {e}")
    exit()

print("Loading YOLO model...")
try:
    model = YOLO("best.pt")
except:
    print("Warning: Using default model yolov8n.pt (Check if your plate can be detected)")
    model = YOLO("yolov8n.pt")

cap = cv2.VideoCapture(CAMERA_ID)
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
cap.set(3, FRAME_WIDTH)
cap.set(4, FRAME_HEIGHT)
CENTER_X = FRAME_WIDTH // 2 

# ==========================================
# Helper Functions
# ==========================================
def smart_sleep(duration):
    """Wait function to prevent window freezing"""
    end_time = time.time() + duration
    while time.time() < end_time:
        cv2.waitKey(30) 
        time.sleep(0.01)

def move_robot_step(cmd, action_name):
    print(f"Car {action_name}")
    ser.write(cmd)
    time.sleep(MOVE_STEP_TIME)
    ser.write(b'S') # Stop immediately after moving

def run_arm_action(command, duration, action_name):
    print(f"Arm: {action_name} ({duration}s)...")
    ser.write(command.encode())
    smart_sleep(duration) # Use smart_sleep
    ser.write(b's')
    time.sleep(0.5)

# ==========================================
# Main Loop
# ==========================================
print(f"System Started! Target Lock Range: {MIN_GRAB_AREA} ~ {MAX_GRAB_AREA}")

try:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: 
            time.sleep(0.1)
            continue

        # 1. YOLO Recognition
        results = model.predict(frame, conf=0.5, verbose=False)
        
        target_box = None
        max_area = 0
        detected_class_name = ""

        for box in results[0].boxes:
            # --- Filter non-plate objects ---
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id]
            
            # If the detected ID is not what we set (e.g., not a plate), skip it
            if cls_id != TARGET_CLASS_ID:
                continue 
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            area = (x2 - x1) * (y2 - y1)
            
            # Draw green box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{cls_name} Area:{int(area)}", (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            if area > max_area:
                max_area = area
                target_box = (x1, x2, y1, y2)
                detected_class_name = cls_name

        # Display current target range info
        cv2.putText(frame, f"TARGET RANGE: {int(MIN_GRAB_AREA)} ~ {int(MAX_GRAB_AREA)}", (10, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        
        status_text = "SEARCHING"

        if target_box:
            x1, x2, y1, y2 = target_box
            cx = (x1 + x2) // 2
            
            cv2.circle(frame, (cx, (y1+y2)//2), 10, (0, 0, 255), -1)
            
            # Draw alignment lines
            cv2.line(frame, (CENTER_X - ALIGN_TOLERANCE, 0), (CENTER_X - ALIGN_TOLERANCE, FRAME_HEIGHT), (0, 255, 255), 1)
            cv2.line(frame, (CENTER_X + ALIGN_TOLERANCE, 0), (CENTER_X + ALIGN_TOLERANCE, FRAME_HEIGHT), (0, 255, 255), 1)

            # --- Navigation Logic (Core Modification) ---
            
            # 1. Align left/right first (Highest priority)
            if cx < (CENTER_X - ALIGN_TOLERANCE):
                status_text = "<< LEFT CORRECT"
                move_robot_step(b'L', "Left Correct")
                
            elif cx > (CENTER_X + ALIGN_TOLERANCE):
                status_text = "RIGHT CORRECT >>"
                move_robot_step(b'R', "Right Correct")
                
            # 2. Aligned left/right, adjust distance
            else:
                # Case A: Too far (Area too small) -> Forward
                if max_area < MIN_GRAB_AREA:
                    status_text = f"FORWARD (Too Far {int(max_area)})"
                    move_robot_step(b'F', "Forward Approach")
                
                # Case B: Too close! (Area too big) -> Backward (Fixes fixed arm length issue)
                elif max_area > MAX_GRAB_AREA:
                    status_text = f"BACK (Too Close {int(max_area)})"
                    # Assuming 'B' is backward in your Arduino code
                    move_robot_step(b'B', "Backward Correct") 
                
                # Case C: Perfect Range (Sweet Spot) -> Grab
                else:
                    status_text = "PERFECT! GRABBING..."
                    cv2.putText(frame, status_text, (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                    cv2.imshow("Robot Vision", frame)
                    cv2.waitKey(1) 
                    
                    print(f"\nEntered Perfect Range ({int(max_area)})! Executing grab...")
                    ser.write(b'S') 
                    time.sleep(1)
                    
                    # Execute Arm Actions
                    run_arm_action('1', TIME_EXTEND,  "Extend")
                    run_arm_action('3', TIME_GRAB,    "Grab")
                    run_arm_action('2', TIME_RETRACT, "Retract")
                    run_arm_action('4', TIME_RELEASE, "Release")
                    
                    print("Mission Complete, resting...")
                    time.sleep(5)
                    break 

        cv2.imshow("Robot Vision", frame)
        if cv2.waitKey(1) == ord('q'):
            break

except KeyboardInterrupt:
    print("Program Interrupted")

finally:
    if 'ser' in locals() and ser.is_open:
        ser.write(b'S')
        ser.close()
    cap.release()
    cv2.destroyAllWindows()
