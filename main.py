import cv2
import time
import sys
from pose_detector import PoseDetector
from motion_detector import MotionDetector
from gamepad_controller import GamepadController
from config import *

class EldenRingMotionControl:
    def __init__(self):
        print("📱 شروع سیستم کنترل حرکتی Elden Ring...")
        
        # نرم‌افزار
        self.pose_detector = PoseDetector()
        self.motion_detector = MotionDetector(self.pose_detector)
        self.gamepad = GamepadController()
        
        # کمره
        self.cap = cv2.VideoCapture(CAMERA_ID)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)
        
        # متغیرهای زمان‌بندی
        self.prev_time = time.time()
        self.fps = 0
        self.frame_count = 0
        
        # موضعیت حرکتی قبلی
        self.prev_landmarks = None
        
        # صاف‌��ردن حرکات
        self.smooth_camera = {'x': 0, 'y': 0}
        
        print("✅ سیستم آماده است!")
        print("\n🎮 دستورات:")
        print("  - راه رفتن: تکان دادن پاها")
        print("  - دویدن: بالا آوردن زانوها")
        print("  - پریدن: پریدن از زمین")
        print("  - حمله سبک: تکان دادن دست آرام")
        print("  - حمله سنگین: تکان دادن دست قوی")
        print("  - جاخالی دادن: خم شدن به جلو")
        print("  - spell: بالا آوردن هر دو دست")
        print("  - آیتم: دست به سمت دهان")
        print("\nQ برای خروج")
    
    def run(self):
        """حلقه اصلی برنامه"""
        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                # تشخیص وضعیت بدن
                if self.pose_detector.detect_pose(frame):
                    
                    # تشخیص حرکات
                    movements = self.motion_detector.detect_movements()
                    
                    # تشخیص حرکت دوربین
                    camera_movement = self.motion_detector.get_camera_movement()
                    
                    # صاف‌کردن حرکت دوربین
                    self.smooth_camera['x'] = (
                        MOTION_SMOOTH_FACTOR * self.smooth_camera['x'] +
                        (1 - MOTION_SMOOTH_FACTOR) * camera_movement['x']
                    )
                    self.smooth_camera['y'] = (
                        MOTION_SMOOTH_FACTOR * self.smooth_camera['y'] +
                        (1 - MOTION_SMOOTH_FACTOR) * camera_movement['y']
                    )
                    
                    # ارسال فرمان به gamepad
                    self.gamepad.process_movements(movements, self.smooth_camera)
                    
                    # نمایش اطلاعات
                    if DISPLAY_SKELETON:
                        frame = self.pose_detector.draw_landmarks(frame)
                    
                    if DISPLAY_ACTIONS:
                        frame = self._draw_actions(frame, movements)
                
                # نمایش FPS
                if DISPLAY_FPS:
                    frame = self._draw_fps(frame)
                
                # نمایش فریم
                cv2.imshow('Elden Ring Motion Control', frame)
                
                # خروج
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                # به روز رسانی landmarks قبلی
                self.motion_detector.update_prev_landmarks()
                
        except KeyboardInterrupt:
            print("\n⛔ متوقف شد...")
        finally:
            self.cleanup()
    
    def _draw_fps(self, frame):
        """رسم FPS روی فریم"""
        current_time = time.time()
        self.frame_count += 1
        
        if current_time - self.prev_time >= 1:
            self.fps = self.frame_count
            self.frame_count = 0
            self.prev_time = current_time
        
        cv2.putText(frame, f'FPS: {self.fps}', (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame
    
    def _draw_actions(self, frame, movements):
        """رسم عملیات فعلی روی فریم"""
        y_offset = 70
        
        actions = []
        if movements['walk']:
            actions.append("🚶 راه رفتن")
        if movements['run']:
            actions.append("🏃 دویدن")
        if movements['jump']:
            actions.append("🦘 پریدن")
        if movements['attack_light']:
            actions.append("⚔️ حمله سبک")
        if movements['attack_heavy']:
            actions.append("🗡️ حمله سنگین")
        if movements['dodge']:
            actions.append("↩️ جاخالی دادن")
        if movements['spell_cast']:
            actions.append("✨ جادو")
        if movements['item_use']:
            actions.append("🍗 آیتم")
        if movements['pose']:
            actions.append("🙏 Gesture")
        
        for action in actions:
            cv2.putText(frame, action, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_offset += 30
        
        return frame
    
    def cleanup(self):
        """تمیز‌کردن منابع"""
        print("\n🛑 بسته شدن...")
        self.cap.release()
        cv2.destroyAllWindows()
        self.pose_detector.release()
        self.gamepad.close()
        print("✅ بسته شد")

def main():
    """تابع اصلی"""
    controller = EldenRingMotionControl()
    controller.run()

if __name__ == "__main__":
    main()
