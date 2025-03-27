# GX - 1700

This project uses a combination of computer vision (for gesture recognition) and Arduino-controlled hardware to create a hand-gesture controlled robot. The laptop-side software (written in Python) captures hand gestures using OpenCV and MediaPipe (or cvzone) and sends commands via Bluetooth to the robot. 

This README explains how to set up the Python environment with the exact package versions needed for the project.

## Python Version Requirement

- **Python:** 3.10.10  
  (Make sure you are using a 64-bit version of Python 3.10.10.)

## Required Python Packages
- In the **requirements.txt** file

## Setup Instructions

### 1. Clone the Repository

Clone the project repository and navigate into the project directory:

```bash
git clone https://github.com/SShogun/GX-1700
cd [<repository-directory>]
```

### 2. Create Virtual Environment
```bash
python3.10 -m venv env
```
### 3. Activate Virtual Environment
- On Windows: 
```bash
env\Scripts\activate
```
- On macOS/Linux: 
```bash
source env/bin/activate
```
4. Upgrade pip
Ensure your pip is up-to-date:
```bash
pip install --upgrade pip
```

5. Intsalled required Packages
```bash
pip install -r requirements.txt
```

6. Verify Installation
```bash
python -c "import cv2, mediapipe, cvzone, pyserial; print('All libraries imported successfully')"
```
