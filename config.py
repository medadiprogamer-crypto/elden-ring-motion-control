# Configuration for Elden Ring Motion Control System

# Camera and Vision Settings
CAMERA_ID = 0
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720
FPS = 30

# Pose Detection Thresholds
POSE_CONFIDENCE_THRESHOLD = 0.5
LANDMARK_CONFIDENCE_THRESHOLD = 0.5

# Motion Detection Sensitivities (0.0 - 1.0)
WALK_THRESHOLD = 0.05
RUN_THRESHOLD = 0.15
JUMP_THRESHOLD = 0.3
ATTACK_LIGHT_THRESHOLD = 0.2
ATTACK_HEAVY_THRESHOLD = 0.4
DODGE_THRESHOLD = 0.25
SPELL_THRESHOLD = 0.3

# Body Part Indices (MediaPipe Pose Landmarks)
NOSE = 0
LEFT_SHOULDER = 11
RIGHT_SHOULDER = 12
LEFT_ELBOW = 13
RIGHT_ELBOW = 14
LEFT_WRIST = 15
RIGHT_WRIST = 16
LEFT_HIP = 23
RIGHT_HIP = 24
LEFT_KNEE = 25
RIGHT_KNEE = 26
LEFT_ANKLE = 27
RIGHT_ANKLE = 28

# Gamepad Settings
GAMEPAD_DEADZONE = 0.1
GAMEPAD_MAX_ANALOG = 1.0

# Camera Control Mode
# 'head' - استفاده از حرکت سر
# 'shoulders' - استفاده از حرکت شانه‌ها
# 'gyro' - استفاده از ژیروسکوپ دسته PS4
CAMERA_CONTROL_MODE = 'head'

# Screen Display
DISPLAY_FPS = True
DISPLAY_SKELETON = True
DISPLAY_ACTIONS = True

# Motion Smoothing
MOTION_SMOOTH_FACTOR = 0.7  # بین 0 و 1، بالاتر = نرم‌تر

# Gesture Timeout (ثانیه)
GESTURE_TIMEOUT = 1.0

# Recording Settings
RECORD_VIDEO = False
RECORD_PATH = 'recordings/'

# Calibration
CALIBRATION_FRAMES = 30
