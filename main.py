import requests
import threading
import urllib3
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle

# Disable SSL Warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURATION ---
DOMAIN = "api.onlinehashcrack.com"
KEY_FILE = "key.txt"
ALGO_MODE = 22000 

# --- CLEAN MODERN THEME ---
C_BG = "#121212"          # Material Background
C_CARD = "#1E1E1E"        # Surface Color
C_PRIMARY = "#BB86FC"     # Soft Purple
C_SECONDARY = "#03DAC6"   # Teal
C_ERROR = "#CF6679"       # Red
C_TEXT = "#FFFFFF"        # White
C_CYAN = "#00E5FF"        # NetSecX Cyan
C_HINT = "#808080"        # Grey

Window.clearcolor = get_color_from_hex(C_BG)

# --- CUSTOM ROUNDED BUTTON ---
class RoundedButton(Button):
    def __init__(self, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0,0,0,0)
        self.custom_bg = get_color_from_hex(bg_color)
        self.color = get_color_from_hex("#000000")
        self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=self.custom_bg)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[6])

class NetSecApp(App):
    def build(self):
        self.title = "NetSecX Console"
        
        # Root Layout
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)

        # 1. HEADER (BRANDING UPDATED)
        header = BoxLayout(orientation='vertical', size_hint=(1, 0.12))
        
        # Main Title "NetSecX"
        lbl_title = Label(
            text="NetSecX", 
            font_size='32sp', 
            bold=True, 
            color=get_color_from_hex(C_CYAN), 
            halign='center'
        )
        
        # Sub Title
        lbl_sub = Label(
            text="[ WPA2 SECURITY AUDIT CONSOLE ]", 
            font_size='12sp', 
            bold=True, 
            color=get_color_from_hex(C_TEXT), 
            halign='center',
            font_name='RobotoMono-Regular' if os.path.exists('RobotoMono-Regular.ttf') else 'Roboto'
        )
        
        header.add_widget(lbl_title)
        header.add_widget(lbl_sub)
        root.add_widget(header)

        # 2. API SECTION
        root.add_widget(Label(text="API Configuration", color=get_color_from_hex(C_HINT), size_hint=(1, 0.04), halign='left', text_size=(Window.width-40, None), font_size='12sp'))
        
        api_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=60)
        
        self.api_input = TextInput(
            hint_text="Paste API Key Here",
            multiline=False,
            write_tab=False,
            background_normal='',
            background_active='',
            background_color=get_color_from_hex(C_CARD),
            foreground_color=get_color_from_hex(C_TEXT),
            cursor_color=get_color_from_hex(C_SECONDARY),
            hint_text_color=get_color_from_hex(C_HINT),
            size_hint=(0.75, 1),
            font_size='14sp',
            padding=[15, 20, 10, 10] 
        )
        
        btn_save = RoundedButton(text="SAVE", bg_color=C_SECONDARY, size_hint=(0.25, 1))
        btn_save.bind(on_press=self.save_key)
        
        api_layout.add_widget(self.api_input)
        api_layout.add_widget(btn_save)
        root.add_widget(api_layout)

        # 3. HASH SECTION
        hash_head = BoxLayout(orientation='horizontal', size_hint=(1, 0.04))
        hash_head.add_widget(Label(text="Target Hashes", color=get_color_from_hex(C_HINT), size_hint=(0.8, 1), halign='left', text_size=(Window.width*0.8, None), font_size='12sp'))
        
        btn_clear = Button(text="Clear", size_hint=(0.2, 1), background_normal='', background_color=(0,0,0,0), color=get_color_from_hex(C_ERROR), bold=True)
        btn_clear.bind(on_press=self.clear_buffer)
        hash_head.add_widget(btn_clear)
        root.add_widget(hash_head)

        self.hash_input = TextInput(
            hint_text="Paste WPA* Hashes (One per line)",
            multiline=True,
            background_normal='',
            background_active='',
            background_color=get_color_from_hex(C_CARD),
            foreground_color=get_color_from_hex(C_TEXT),
            cursor_color=get_color_from_hex(C_PRIMARY),
            hint_text_color=get_color_from_hex(C_HINT),
            size_hint=(1, 0.3),
            padding=[10, 10, 10, 10]
        )
        root.add_widget(self.hash_input)

        # 4. ACTION BUTTON
        self.btn_upload = RoundedButton(text="UPLOAD TASKS", bg_color=C_PRIMARY, size_hint=(1, 0.1))
        self.btn_upload.font_size = '16sp'
        self.btn_upload.bind(on_press=self.start_upload_thread)
        root.add_widget(self.btn_upload)

        # 5. TERMINAL
        log_head = BoxLayout(orientation='horizontal', size_hint=(1, 0.04))
        log_head.add_widget(Label(text="System Terminal", color=get_color_from_hex(C_HINT), size_hint=(0.8, 1), halign='left', text_size=(Window.width*0.8, None), font_size='12sp'))
        
        btn_purge = Button(text="Purge", size_hint=(0.2, 1), background_normal='', background_color=(0,0,0,0), color=get_color_from_hex(C_ERROR), bold=True)
        btn_purge.bind(on_press=self.clear_logs)
        log_head.add_widget(btn_purge)
        root.add_widget(log_head)

        self.logs = TextInput(
            text="> NetSecX System Ready...\n",
            readonly=True,
            background_normal='',
            background_active='',
            background_color=get_color_from_hex("#000000"),
            foreground_color=get_color_from_hex("#00FF00"),
            size_hint=(1, 0.25),
            font_size='12sp',
            font_name='RobotoMono-Regular' if os.path.exists('RobotoMono-Regular.ttf') else 'Roboto',
            padding=[10, 10, 10, 10]
        )
        root.add_widget(self.logs)

        # 6. STATUS BAR & FOOTER
        footer_layout = BoxLayout(orientation='vertical', size_hint=(1, 0.08))
        
        self.status_bar = Label(
            text="Status: Idle",
            font_size='11sp',
            color=get_color_from_hex(C_HINT),
            size_hint=(1, 0.5)
        )
        
        # Footer
        lbl_footer = Label(
            text="[ CREATED BY ZERO ]", 
            font_size='10sp', 
            color=get_color_from_hex(C_SECONDARY),
            size_hint=(1, 0.5),
            bold=True
        )
        
        footer_layout.add_widget(self.status_bar)
        footer_layout.add_widget(lbl_footer)
        root.add_widget(footer_layout)

        self.load_saved_key()
        return root

    # --- LOGIC ---
    def log(self, msg):
        Clock.schedule_once(lambda dt: self._update_log(msg))

    def _update_log(self, msg):
        self.logs.text += f"> {msg}\n"

    def clear_logs(self, instance):
        self.logs.text = "> Logs Purged.\n"

    def clear_buffer(self, instance):
        self.hash_input.text = ""

    def update_status(self, text, color=C_HINT):
        self.status_bar.text = f"Status: {text}"
        self.status_bar.color = get_color_from_hex(color)

    def save_key(self, instance):
        key = self.api_input.text.strip()
        if key:
            try:
                with open(KEY_FILE, "w") as f: f.write(key)
                self.log("API Key Saved.")
                self.update_status("Config Saved", C_SECONDARY)
            except: pass

    def load_saved_key(self):
        if os.path.exists(KEY_FILE):
            try:
                with open(KEY_FILE, "r") as f: self.api_input.text = f.read().strip()
                self.log("Saved Key Loaded.")
            except: pass

    def start_upload_thread(self, instance):
        self.btn_upload.text = "Working..."
        self.update_status("Uploading...", C_PRIMARY)
        threading.Thread(target=self.run_upload).start()

    def run_upload(self):
        try:
            api_key = self.api_input.text.strip()
            raw_text = self.hash_input.text
            hash_list = [line.strip() for line in raw_text.splitlines() if line.strip()]

            if not api_key:
                self.log("Error: Please Enter API Key.")
                self.reset_btn()
                return
            
            if not hash_list:
                self.log("Error: No Hashes to upload.")
                self.reset_btn()
                return

            self.log(f"Processing {len(hash_list)} hashes...")
            
            url = f"https://{DOMAIN}/v2"
            headers = {"Content-Type": "application/json", "User-Agent": "NetSecX/7.0"}
            payload = {"api_key": api_key, "agree_terms": "yes", "algo_mode": ALGO_MODE, "hashes": hash_list, "action": "add_tasks"}

            response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log("Success! Uploaded.")
                    self.log(f"Server: {data.get('message')}")
                    self.update_status("Success", C_SECONDARY)
                else:
                    self.log(f"Rejected: {data.get('message')}")
                    self.update_status("Error", C_ERROR)
            else:
                self.log(f"Failed: {response.status_code}")
                self.update_status("Connection Failed", C_ERROR)

        except Exception as e:
            self.log(f"Error: {str(e)}")
            self.update_status("Crashed", C_ERROR)
        
        finally:
            self.reset_btn()

    def reset_btn(self):
        Clock.schedule_once(lambda dt: self._reset_btn_ui())

    def _reset_btn_ui(self):
        self.btn_upload.text = "UPLOAD TASKS"
        if "Success" not in self.status_bar.text: self.update_status("Idle", C_HINT)

if __name__ == '__main__':
    NetSecApp().run()