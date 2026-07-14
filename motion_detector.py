import numpy as np
import time
from config import *

class MotionDetector:
    def __init__(self, pose_detector):
        self.pose = pose_detector
        self.prev_landmarks = None
        self.last_action_time = {}
        self.gesture_start_time = None
        self.current_gesture = None
        
    def detect_movements(self):
        """تشخیص تمام حرکات"""
        movements = {
            'walk': False,
            'run': False,
            'jump': False,
            'attack_light': False,
            'attack_heavy': False,
            'dodge': False,
            'spell_cast': False,
            'item_use': False,
            'pose': False
        }
        
        # حرکت پاها
        movements['walk'] = self.detect_walk()
        movements['run'] = self.detect_run()
        movements['jump'] = self.detect_jump()
        
        # حرکت دست‌ها
        movements['attack_light'] = self.detect_light_attack()
        movements['attack_heavy'] = self.detect_heavy_attack()
        
        # حرکت بدن
        movements['dodge'] = self.detect_dodge()
        movements['spell_cast'] = self.detect_spell()
        movements['item_use'] = self.detect_item_use()
        movements['pose'] = self.detect_pose_gesture()
        
        return movements
    
    def detect_walk(self):
        """تشخیص راه رفتن - تکان دادن پاها در جای خود"""
        left_knee = self.pose.get_landmark(LEFT_KNEE)
        right_knee = self.pose.get_landmark(RIGHT_KNEE)
        left_ankle = self.pose.get_landmark(LEFT_ANKLE)
        right_ankle = self.pose.get_landmark(RIGHT_ANKLE)
        
        if not all([left_knee, right_knee, left_ankle, right_ankle]):
            return False
        
        # محاسبه فاصله بین زانو و مچ پا
        left_leg_distance = abs(left_knee['y'] - left_ankle['y'])
        right_leg_distance = abs(right_knee['y'] - right_ankle['y'])
        
        # اگر پاها تکان می‌خورند اما جسم در جای خود است
        leg_movement = (left_leg_distance + right_leg_distance) / 2
        
        return leg_movement > WALK_THRESHOLD
    
    def detect_run(self):
        """تشخیص دویدن - بالا آوردن زانوها"""
        left_knee = self.pose.get_landmark(LEFT_KNEE)
        right_knee = self.pose.get_landmark(RIGHT_KNEE)
        left_hip = self.pose.get_landmark(LEFT_HIP)
        right_hip = self.pose.get_landmark(RIGHT_HIP)
        
        if not all([left_knee, right_knee, left_hip, right_hip]):
            return False
        
        # اگر زانوها بالاتر از میانه قسمت کمر باشند
        left_knee_up = left_knee['y'] < left_hip['y'] - RUN_THRESHOLD
        right_knee_up = right_knee['y'] < right_hip['y'] - RUN_THRESHOLD
        
        return left_knee_up or right_knee_up
    
    def detect_jump(self):
        """تشخیص پریدن - بلند شدن از زمین"""
        left_ankle = self.pose.get_landmark(LEFT_ANKLE)
        right_ankle = self.pose.get_landmark(RIGHT_ANKLE)
        nose = self.pose.get_landmark(NOSE)
        
        if not all([left_ankle, right_ankle, nose]):
            return False
        
        # اگر پاها از بالای قسمت خاصی بالاتر باشند
        ankles_y = (left_ankle['y'] + right_ankle['y']) / 2
        jump_detected = ankles_y < (nose['y'] - JUMP_THRESHOLD)
        
        return jump_detected
    
    def detect_light_attack(self):
        """تشخیص حمله سبک - تکان دادن دست با سرعت کم"""
        left_wrist = self.pose.get_landmark(LEFT_WRIST)
        right_wrist = self.pose.get_landmark(RIGHT_WRIST)
        left_elbow = self.pose.get_landmark(LEFT_ELBOW)
        right_elbow = self.pose.get_landmark(RIGHT_ELBOW)
        
        if not all([left_wrist, right_wrist, left_elbow, right_elbow]):
            return False
        
        # محاسبه فاصله حرکت دست
        left_wrist_movement = np.sqrt(
            (left_wrist['x'] - left_elbow['x'])**2 + 
            (left_wrist['y'] - left_elbow['y'])**2
        )
        right_wrist_movement = np.sqrt(
            (right_wrist['x'] - right_elbow['x'])**2 + 
            (right_wrist['y'] - right_elbow['y'])**2
        )
        
        max_movement = max(left_wrist_movement, right_wrist_movement)
        
        # حرکت متوسط = حمله سبک
        return ATTACK_LIGHT_THRESHOLD < max_movement < ATTACK_HEAVY_THRESHOLD
    
    def detect_heavy_attack(self):
        """تشخیص حمله سنگین - تکان دادن دست قوی"""
        left_wrist = self.pose.get_landmark(LEFT_WRIST)
        right_wrist = self.pose.get_landmark(RIGHT_WRIST)
        left_elbow = self.pose.get_landmark(LEFT_ELBOW)
        right_elbow = self.pose.get_landmark(RIGHT_ELBOW)
        
        if not all([left_wrist, right_wrist, left_elbow, right_elbow]):
            return False
        
        left_wrist_movement = np.sqrt(
            (left_wrist['x'] - left_elbow['x'])**2 + 
            (left_wrist['y'] - left_elbow['y'])**2
        )
        right_wrist_movement = np.sqrt(
            (right_wrist['x'] - right_elbow['x'])**2 + 
            (right_wrist['y'] - right_elbow['y'])**2
        )
        
        max_movement = max(left_wrist_movement, right_wrist_movement)
        
        return max_movement > ATTACK_HEAVY_THRESHOLD
    
    def detect_dodge(self):
        """تشخیص جاخالی دادن - خم شدن به جلو"""
        left_shoulder = self.pose.get_landmark(LEFT_SHOULDER)
        right_shoulder = self.pose.get_landmark(RIGHT_SHOULDER)
        left_hip = self.pose.get_landmark(LEFT_HIP)
        right_hip = self.pose.get_landmark(RIGHT_HIP)
        
        if not all([left_shoulder, right_shoulder, left_hip, right_hip]):
            return False
        
        # محاسبه زاویه خمیدگی بدن
        shoulder_y = (left_shoulder['y'] + right_shoulder['y']) / 2
        hip_y = (left_hip['y'] + right_hip['y']) / 2
        
        # اگر شانه‌ها به سمت پایین‌تر از ران‌ها باشند
        bend_detected = shoulder_y > hip_y + DODGE_THRESHOLD
        
        return bend_detected
    
    def detect_spell(self):
        """تشخیص spell casting - حرکات متوازن"""
        left_wrist = self.pose.get_landmark(LEFT_WRIST)
        right_wrist = self.pose.get_landmark(RIGHT_WRIST)
        left_shoulder = self.pose.get_landmark(LEFT_SHOULDER)
        right_shoulder = self.pose.get_landmark(RIGHT_SHOULDER)
        
        if not all([left_wrist, right_wrist, left_shoulder, right_shoulder]):
            return False
        
        # اگر دستان در سطح شانه یا بالاتر باشند
        left_raised = left_wrist['y'] < left_shoulder['y'] - SPELL_THRESHOLD
        right_raised = right_wrist['y'] < right_shoulder['y'] - SPELL_THRESHOLD
        
        return left_raised and right_raised
    
    def detect_item_use(self):
        """تشخیص استفاده از آیتم - حرکت یکی از دست‌ها به سمت دهان"""
        left_wrist = self.pose.get_landmark(LEFT_WRIST)
        right_wrist = self.pose.get_landmark(RIGHT_WRIST)
        nose = self.pose.get_landmark(NOSE)
        
        if not all([left_wrist, right_wrist, nose]):
            return False
        
        left_near_mouth = (
            abs(left_wrist['x'] - nose['x']) < 0.15 and
            abs(left_wrist['y'] - nose['y']) < 0.1
        )
        
        right_near_mouth = (
            abs(right_wrist['x'] - nose['x']) < 0.15 and
            abs(right_wrist['y'] - nose['y']) < 0.1
        )
        
        return left_near_mouth or right_near_mouth
    
    def detect_pose_gesture(self):
        """تشخیص gesture بدن"""
        # یک pose خاص: دستان روی سینه
        left_wrist = self.pose.get_landmark(LEFT_WRIST)
        right_wrist = self.pose.get_landmark(RIGHT_WRIST)
        nose = self.pose.get_landmark(NOSE)
        
        if not all([left_wrist, right_wrist, nose]):
            return False
        
        # اگر هر دو دست روی سینه باشند
        return (left_wrist['y'] > nose['y'] and 
                right_wrist['y'] > nose['y'])
    
    def get_camera_movement(self):
        """محاسبه حرکت دوربین بر اساس حرکت سر یا شانه‌ها"""
        if CAMERA_CONTROL_MODE == 'head':
            return self._get_head_movement()
        elif CAMERA_CONTROL_MODE == 'shoulders':
            return self._get_shoulders_movement()
        return {'x': 0, 'y': 0}
    
    def _get_head_movement(self):
        """حرکت دوربین بر اساس سر"""
        nose = self.pose.get_landmark(NOSE)
        left_ear = self.pose.get_landmark(3)  # Left Ear
        right_ear = self.pose.get_landmark(4)  # Right Ear
        
        if not all([nose, left_ear, right_ear]):
            return {'x': 0, 'y': 0}
        
        # محاسبه زاویه سر (چپ/راست)
        horizontal = right_ear['x'] - left_ear['x']
        
        # محاسبه خمیدگی سر (بالا/پایین)
        vertical = nose['y'] - (left_ear['y'] + right_ear['y']) / 2
        
        return {
            'x': horizontal,  # منفی = چپ، مثبت = راست
            'y': vertical     # منفی = بالا، مثبت = پایین
        }
    
    def _get_shoulders_movement(self):
        """حرکت دوربین بر اساس شانه‌ها"""
        left_shoulder = self.pose.get_landmark(LEFT_SHOULDER)
        right_shoulder = self.pose.get_landmark(RIGHT_SHOULDER)
        
        if not (left_shoulder and right_shoulder):
            return {'x': 0, 'y': 0}
        
        # اگر شانه چپ بالاتر باشد = فرد سر را به چپ تکان داده
        shoulder_tilt = left_shoulder['y'] - right_shoulder['y']
        
        # اگر شانه‌ها بالا باشند
        shoulder_height = (left_shoulder['y'] + right_shoulder['y']) / 2
        
        return {
            'x': shoulder_tilt,   # منفی = بالا رفتن شانه چپ
            'y': shoulder_height
        }
    
    def update_prev_landmarks(self):
        """به روز رسانی landmarks قبلی"""
        if self.pose.landmarks:
            self.prev_landmarks = [
                type('obj', (object,), {
                    'x': lm.x, 'y': lm.y, 'z': lm.z, 'visibility': lm.visibility
                })()
                for lm in self.pose.landmarks
            ]
