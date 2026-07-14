import vgamepad as vg
import time
from config import *

class GamepadController:
    def __init__(self):
        self.gamepad = vg.VX360Gamepad()
        self.last_input_time = {}
        self.input_cooldown = 0.1  # ثانیه
        
        # نقشه‌برداری حرکات به دستورات Elden Ring
        self.action_map = {
            'walk': self._handle_walk,
            'run': self._handle_run,
            'jump': self._handle_jump,
            'attack_light': self._handle_light_attack,
            'attack_heavy': self._handle_heavy_attack,
            'dodge': self._handle_dodge,
            'spell_cast': self._handle_spell,
            'item_use': self._handle_item_use,
            'pose': self._handle_pose,
        }
        
        # حالت جاری
        self.is_running = False
        self.is_walking = False
    
    def process_movements(self, movements, camera_movement):
        """پردازش حرکات و تبدیل به input gamepad"""
        
        # کنترل حرکت
        if movements['run']:
            self._handle_run()
            self.is_running = True
            self.is_walking = False
        elif movements['walk']:
            self._handle_walk()
            self.is_running = False
            self.is_walking = True
        else:
            # توقف حرکت
            self.gamepad.right_trigger_float(0.0)
            self.gamepad.left_joystick_float(0.0, 0.0)
            self.is_running = False
            self.is_walking = False
        
        # کنترل حمله
        if movements['attack_heavy']:
            self._handle_heavy_attack()
        elif movements['attack_light']:
            self._handle_light_attack()
        
        # کنترل دفاع
        if movements['dodge']:
            self._handle_dodge()
        
        # کنترل جادو
        if movements['spell_cast']:
            self._handle_spell()
        
        # استفاده از آیتم
        if movements['item_use']:
            self._handle_item_use()
        
        # pose/gesture
        if movements['pose']:
            self._handle_pose()
        
        # کنترل دوربین
        self._handle_camera_movement(camera_movement)
        
        # ارسال input
        self.gamepad.update()
    
    def _handle_walk(self):
        """راه رفتن - Stick چپ"""
        # استفاده از L3 (پایین trigger کردن چپ)
        self.gamepad.left_joystick_float(0.5, 0.5)  # حرکت جلو
        self.gamepad.right_trigger_float(0.0)  # دویدن نیست
    
    def _handle_run(self):
        """دویدن - راه رفتن + دویدن"""
        self.gamepad.left_joystick_float(0.5, 0.5)  # حرکت جلو
        self.gamepad.right_trigger_float(1.0)  # دویدن (hold RT)
    
    def _handle_jump(self):
        """پریدن - دکمه Space (A)"""
        if self._check_cooldown('jump'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            time.sleep(0.05)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
            self.gamepad.update()
            self.last_input_time['jump'] = time.time()
    
    def _handle_light_attack(self):
        """حمله سبک - X دکمه"""
        if self._check_cooldown('attack_light'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_X)
            self.gamepad.update()
            self.last_input_time['attack_light'] = time.time()
    
    def _handle_heavy_attack(self):
        """حمله سنگین - Y دکمه"""
        if self._check_cooldown('attack_heavy'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            self.gamepad.update()
            time.sleep(0.15)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_Y)
            self.gamepad.update()
            self.last_input_time['attack_heavy'] = time.time()
    
    def _handle_dodge(self):
        """جاخالی دادن - B دکمه"""
        if self._check_cooldown('dodge'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            self.gamepad.update()
            time.sleep(0.05)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_B)
            self.gamepad.update()
            self.last_input_time['dodge'] = time.time()
    
    def _handle_spell(self):
        """spell casting - RB دکمه"""
        if self._check_cooldown('spell'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RB)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_RB)
            self.gamepad.update()
            self.last_input_time['spell'] = time.time()
    
    def _handle_item_use(self):
        """استفاده از آیتم - LB دکمه"""
        if self._check_cooldown('item'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LB)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_LB)
            self.gamepad.update()
            self.last_input_time['item'] = time.time()
    
    def _handle_pose(self):
        """gesture/pose - START یا دکمه menu"""
        if self._check_cooldown('pose'):
            self.gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            self.gamepad.update()
            time.sleep(0.1)
            self.gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_START)
            self.gamepad.update()
            self.last_input_time['pose'] = time.time()
    
    def _handle_camera_movement(self, camera_movement):
        """کنترل دوربین - Right Stick"""
        if camera_movement:
            # محدود کردن حرکت
            x = max(-1.0, min(1.0, camera_movement['x'] * 2))
            y = max(-1.0, min(1.0, camera_movement['y'] * 2))
            
            self.gamepad.right_joystick_float(x, y)
    
    def _check_cooldown(self, action):
        """بررسی cooldown برای یک action"""
        current_time = time.time()
        if action in self.last_input_time:
            if current_time - self.last_input_time[action] < self.input_cooldown:
                return False
        return True
    
    def press_button(self, button):
        """فشردن یک دکمه"""
        self.gamepad.press_button(button)
        self.gamepad.update()
        time.sleep(0.05)
        self.gamepad.release_button(button)
        self.gamepad.update()
    
    def set_analog_stick(self, side, x, y):
        """تنظیم analog stick"""
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        if side == 'left':
            self.gamepad.left_joystick_float(x, y)
        elif side == 'right':
            self.gamepad.right_joystick_float(x, y)
        
        self.gamepad.update()
    
    def set_triggers(self, left, right):
        """تنظیم trigger‌ها"""
        self.gamepad.left_trigger_float(max(0.0, min(1.0, left)))
        self.gamepad.right_trigger_float(max(0.0, min(1.0, right)))
        self.gamepad.update()
    
    def reset(self):
        """ریست کردن همه دکمه‌ها"""
        self.gamepad.reset()
        self.gamepad.update()
        self.is_running = False
        self.is_walking = False
    
    def close(self):
        """بستن gamepad"""
        self.reset()
