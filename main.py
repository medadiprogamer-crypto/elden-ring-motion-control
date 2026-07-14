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
        
        # صاف‌کردن حرکات
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
                    print("⚠️ خطا در خواندن فریم از دوربین")
                    break
                
                try:
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
                        try:
                            self.gamepad.process_movements(movements, self.smooth_camera)
                        except Exception as e:
                            print(f"⚠️ خطا در gamepad: {e}")
                        
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
                    
                except Exception as e:
                    print(f"⚠️ خطا در حلقه اصلی: {e}")
                    continue
                
        except KeyboardInterrupt:
            print("\n⛔ متوقف شد...")
        except Exception as e:
            print(f"⚠️ خطای کلی: {e}")
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
        
        fps_text = 'FPS: {}'.format(self.fps)
        cv2.putText(frame, fps_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        return frame
    
    def _draw_actions(self, frame, movements):
        """رسم عملیات فعلی روی فریم"""
        y_offset = 70
        
        actions = []
        if movements['walk']:
            actions.append("Walk")
        if movements['run']:
            actions.append("Run")
        if movements['jump']:
            actions.append("Jump")
        if movements['attack_light']:
            actions.append("Light Attack")
        if movements['attack_heavy']:
            actions.append("Heavy Attack")
        if movements['dodge']:
            actions.append("Dodge")
        if movements['spell_cast']:
            actions.append("Spell")
        if movements['item_use']:
            actions.append("Item")
        if movements['pose']:
            actions.append("Gesture")
        
        for action in actions:
            cv2.putText(frame, action, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            y_offset += 30
        
        return frame
    
    def cleanup(self):
        """تمیز‌کردن منابع"""
        print("\n🛑 بسته شدن...")
        try:
            self.cap.release()
            cv2.destroyAllWindows()
            self.pose_detector.release()
            self.gamepad.close()
        except Exception as e:
            print(f"⚠️ خطا در بسته شدن: {e}")
        print("✅ بسته شد")

def main():
    """تابع اصلی"""
    controller = EldenRingMotionControl()
    controller.run()

if __name__ == "__main__":
    main()
