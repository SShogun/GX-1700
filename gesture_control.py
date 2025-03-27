import cv2
import mediapipe as mp
import serial
import time

# --- Serial (Bluetooth) Setup ---
# Adjust 'COM3' to your actual port (e.g., 'COM5', '/dev/ttyUSB0', etc.)
try:
    ser = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)  # Wait for connection to establish
    print("Serial connection established successfully")
except Exception as e:
    print("Error initializing serial connection:", e)
    ser = None

# --- MediaPipe Hands Setup ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize Hands (set max_num_hands=1 for single hand)
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# --- OpenCV Camera Setup ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
else:
    print("Camera initialized successfully")

def fingers_status(hand_landmarks, image_width, image_height):
    """
    Returns a list of 5 binary values [thumb, index, middle, ring, pinky],
    indicating whether each finger is extended (1) or not (0).
    This is a basic approach using landmark positions.
    Adjust logic if you want more advanced detection.
    """

    # Landmark indices for reference:
    # 0: wrist
    # 1..4: thumb
    # 5..8: index
    # 9..12: middle
    # 13..16: ring
    # 17..20: pinky

    # Convert normalized coordinates to pixel values
    def landmark_px(lm):
        return int(lm.x * image_width), int(lm.y * image_height)

    # Helper: check if a finger tip is above its PIP joint
    # for vertical alignment. For thumb, we use a different approach.
    fingers = [0, 0, 0, 0, 0]

    # Indices in the landmarks array
    thumb_tip = hand_landmarks.landmark[4]
    thumb_ip = hand_landmarks.landmark[3]
    index_tip = hand_landmarks.landmark[8]
    index_pip = hand_landmarks.landmark[6]
    middle_tip = hand_landmarks.landmark[12]
    middle_pip = hand_landmarks.landmark[10]
    ring_tip = hand_landmarks.landmark[16]
    ring_pip = hand_landmarks.landmark[14]
    pinky_tip = hand_landmarks.landmark[20]
    pinky_pip = hand_landmarks.landmark[18]

    # Convert them to pixel coords
    thumb_tip_x, thumb_tip_y = landmark_px(thumb_tip)
    thumb_ip_x, thumb_ip_y = landmark_px(thumb_ip)
    index_tip_x, index_tip_y = landmark_px(index_tip)
    index_pip_x, index_pip_y = landmark_px(index_pip)
    middle_tip_x, middle_tip_y = landmark_px(middle_tip)
    middle_pip_x, middle_pip_y = landmark_px(middle_pip)
    ring_tip_x, ring_tip_y = landmark_px(ring_tip)
    ring_pip_x, ring_pip_y = landmark_px(ring_pip)
    pinky_tip_x, pinky_tip_y = landmark_px(pinky_tip)
    pinky_pip_x, pinky_pip_y = landmark_px(pinky_pip)

    # Thumb logic (assuming a right hand in mirror):
    # If thumb_tip is to the left of the thumb_ip (for a mirrored image),
    # we consider the thumb extended.
    if thumb_tip_x < thumb_ip_x:
        fingers[0] = 1

    # Index finger
    if index_tip_y < index_pip_y:
        fingers[1] = 1

    # Middle finger
    if middle_tip_y < middle_pip_y:
        fingers[2] = 1

    # Ring finger
    if ring_tip_y < ring_pip_y:
        fingers[3] = 1

    # Pinky
    if pinky_tip_y < pinky_pip_y:
        fingers[4] = 1

    return fingers

def interpret_gesture(fingers):
    """
    Convert the [thumb, index, middle, ring, pinky] array into a command.
    Example mappings:
      Only index -> 'F' (Forward)
      Only thumb -> 'L' (Left)
      Index+Middle -> 'R' (Right)
      Only pinky -> 'B' (Backward)
      All down (fist) -> 'S' (Stop)
    """
    if fingers == [0, 1, 0, 0, 0]:
        return 'F'
    elif fingers == [1, 0, 0, 0, 0]:
        return 'L'
    elif fingers == [0, 1, 1, 0, 0]:
        return 'R'
    elif fingers == [0, 0, 0, 0, 1]:
        return 'B'
    elif fingers == [0, 0, 0, 0, 0]:
        return 'S'
    else:
        return None

# For tracking last command to avoid spamming terminal
last_command = None
print("Starting gesture recognition. Press 'Esc' to exit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera read error.")
        break

    frame = cv2.flip(frame, 1)  # mirror horizontally
    h, w, c = frame.shape

    # Convert to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture_command = None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks on frame
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            # Analyze finger states
            fingers = fingers_status(hand_landmarks, w, h)
            # Interpret gesture
            gesture_command = interpret_gesture(fingers)
            if gesture_command:
                # Display gesture text
                cv2.putText(frame, f"Gesture: {gesture_command}", (10, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                
                # Print command in terminal with description
                command_descriptions = {
                    'F': 'Forward',
                    'L': 'Left',
                    'R': 'Right',
                    'B': 'Backward',
                    'S': 'Stop'
                }
                
                # Only print if command changed to avoid flooding terminal
                if gesture_command != last_command:
                    description = command_descriptions.get(gesture_command, 'Unknown')
                    print(f"Detected: {gesture_command} ({description})")
                    last_command = gesture_command
                
                break  # Process only the first detected hand
    else:
        # Reset last command when no hand is detected
        if last_command is not None:
            print("No hand detected")
            last_command = None

    # Send gesture command over serial if we have one
    if gesture_command and ser:
        try:
            ser.write(gesture_command.encode())
            print(f"Sent to device: {gesture_command}")
        except Exception as e:
            print(f"Serial communication error: {e}")

    cv2.imshow("Hand Gesture Recognition", frame)
    # Press 'Esc' to exit
    if cv2.waitKey(1) & 0xFF == 27:
        print("Exiting program...")
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
hands.close()
if ser:
    ser.close()
print("Program terminated successfully")