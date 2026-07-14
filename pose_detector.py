import cv2
import mediapipe as mp
import numpy as np
from config import *

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            smooth_segmentation=False,
            min_detection_confidence=POSE_CONFIDENCE_THRESHOLD,
            min_tracking_confidence=LANDMARK_CONFIDENCE_THRESHOLD
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.landmarks = None
        
    def detect_pose(self, frame):
        """تشخیص وضعیت بدن در فریم"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        
        if results.pose_landmarks:
            self.landmarks = results.pose_landmarks.landmark
            return True
        return False
    
    def get_landmark(self, index):
        """دریافت مختصات یک landmark"""
        if self.landmarks and index < len(self.landmarks):
            landmark = self.landmarks[index]
            return {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
        return None
    
    def get_all_landmarks(self):
        """دریافت تمام landmarks"""
        if self.landmarks:
            return [(lm.x, lm.y, lm.z) for lm in self.landmarks]
        return None
    
    def distance_between(self, index1, index2):
        """محاسبه فاصله بین دو نقطه"""
        p1 = self.get_landmark(index1)
        p2 = self.get_landmark(index2)
        
        if p1 and p2:
            dx = p2['x'] - p1['x']
            dy = p2['y'] - p1['y']
            dz = p2['z'] - p1['z']
            return np.sqrt(dx**2 + dy**2 + dz**2)
        return 0
    
    def angle_between(self, index1, index2, index3):
        """محاسبه زاویه بین سه نقطه (vertex در وسط)"""
        p1 = self.get_landmark(index1)
        p2 = self.get_landmark(index2)
        p3 = self.get_landmark(index3)
        
        if not (p1 and p2 and p3):
            return 0
        
        a = np.array([p1['x'], p1['y'], p1['z']])
        b = np.array([p2['x'], p2['y'], p2['z']])
        c = np.array([p3['x'], p3['y'], p3['z']])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
        angle = np.arccos(np.clip(cosine_angle, -1, 1))
        return np.degrees(angle)
    
    def draw_landmarks(self, frame):
        """رسم landmarks روی فریم"""
        if self.landmarks:
            h, w, c = frame.shape
            for idx, landmark in enumerate(self.landmarks):
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                if landmark.visibility > LANDMARK_CONFIDENCE_THRESHOLD:
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
        
        return frame
    
    def get_body_velocity(self, prev_landmarks):
        """محاسبه سرعت بدن بر اساس تغییر موقعیت"""
        if not (self.landmarks and prev_landmarks):
            return 0
        
        total_distance = 0
        count = 0
        
        for i in range(len(self.landmarks)):
            curr = self.landmarks[i]
            prev = prev_landmarks[i]
            
            if curr.visibility > LANDMARK_CONFIDENCE_THRESHOLD:
                dx = curr.x - prev.x
                dy = curr.y - prev.y
                dz = curr.z - prev.z
                distance = np.sqrt(dx**2 + dy**2 + dz**2)
                total_distance += distance
                count += 1
        
        return total_distance / (count + 1e-6) if count > 0 else 0
    
    def is_standing(self):
        """برر��ی اینکه آیا فرد ایستاده است"""
        # اگر بدن نسبتاً ثابت است
        return True
    
    def get_body_forward_direction(self):
        """دریافت جهت رو به جلو بدن"""
        left_shoulder = self.get_landmark(LEFT_SHOULDER)
        right_shoulder = self.get_landmark(RIGHT_SHOULDER)
        
        if left_shoulder and right_shoulder:
            # جهت میان شانه‌ها
            return {
                'x': (right_shoulder['x'] + left_shoulder['x']) / 2,
                'y': (right_shoulder['y'] + left_shoulder['y']) / 2
            }
        return None
    
    def release(self):
        """آزاد کردن منابع"""
        self.pose.close()
