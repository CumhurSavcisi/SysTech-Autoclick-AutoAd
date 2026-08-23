import time
import threading
import json
import os
import customtkinter as ctk
from pynput.mouse import Controller, Button
from pynput.keyboard import Listener, KeyCode, Key, Controller as KeyboardController

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

mouse = Controller()
keyboard = KeyboardController()

is_clicking = False
is_ad_running = False

CONFIG_FILE = "config.json"

class AutoClickerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SysTech #HERZAMANTÜRETMECELİK")
        self.geometry("520x740")
        self.resizable(False, False)

        self.tabview = ctk.CTkTabview(self, fg_color="#1a2b4c")
        self.tabview.pack(pady=10, padx=10, fill="both", expand=True)

        self.tab_clicker = self.tabview.add("Blok Makrosu / Auto Clicker")
        self.tab_ads = self.tabview.add("Reklam Makrosu")

        self.setup_clicker_tab()
        self.setup_ads_tab()
        self.load_settings()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_clicker_tab(self):
        self.key_frame = ctk.CTkFrame(self.tab_clicker, fg_color="#14213d")
        self.key_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.key_frame, text="Çalıştırma Tuşu (Keybind)", text_color="#66b3ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))

        self.keys_list = ["f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12", "space"]
        self.key_dropdown = ctk.CTkComboBox(self.key_frame, values=self.keys_list, command=self.update_keybind)
        self.key_dropdown.set("f6")
        self.key_dropdown.pack(fill="x", padx=10, pady=10)
        self.selected_key = "f6"

        self.mouse_frame = ctk.CTkFrame(self.tab_clicker, fg_color="#14213d")
        self.mouse_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.mouse_frame, text="Mouse Tuşu", text_color="#66b3ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))

        self.mouse_var = ctk.StringVar(value="Sol")
        ctk.CTkRadioButton(self.mouse_frame, text="Sol Tık", variable=self.mouse_var, value="Sol").pack(side="left", padx=15, pady=10)
        ctk.CTkRadioButton(self.mouse_frame, text="Sağ Tık", variable=self.mouse_var, value="Sağ").pack(side="left", padx=15, pady=10)
        ctk.CTkRadioButton(self.mouse_frame, text="Orta Tık", variable=self.mouse_var, value="Orta").pack(side="left", padx=15, pady=10)

        self.mode_frame = ctk.CTkFrame(self.tab_clicker, fg_color="#14213d")
        self.mode_frame.pack(pady=5, padx=10, fill="x")
        ctk.CTkLabel(self.mode_frame, text="Çalışma Modu", text_color="#66b3ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))

        self.mode_var = ctk.StringVar(value="Toggle")
        ctk.CTkRadioButton(self.mode_frame, text="Tek Tek (Aç/Kapat)", variable=self.mode_var, value="Toggle").pack(side="left", padx=15, pady=10)
        ctk.CTkRadioButton(self.mode_frame, text="Basılı Tut", variable=self.mode_var, value="Hold").pack(side="left", padx=15, pady=10)

        self.settings_frame = ctk.CTkFrame(self.tab_clicker, fg_color="#14213d")
        self.settings_frame.pack(pady=5, padx=10, fill="x")

        self.cps_label = ctk.CTkLabel(self.settings_frame, text="Tıklama Hızı (CPS): 10", text_color="#ffffff")
        self.cps_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.cps_slider = ctk.CTkSlider(self.settings_frame, from_=1, to=50, number_of_steps=49, command=self.update_cps_label)
        self.cps_slider.set(10)
        self.cps_slider.pack(fill="x", padx=10, pady=10)

        self.limit_label = ctk.CTkLabel(self.settings_frame, text="Tıklama Limiti (0 = Sınırsız):", text_color="#ffffff")
        self.limit_label.pack(anchor="w", padx=10, pady=(5, 0))
        self.limit_entry = ctk.CTkEntry(self.settings_frame)
        self.limit_entry.insert(0, "0")
        self.limit_entry.pack(fill="x", padx=10, pady=(0, 10))

        self.clicker_status = ctk.CTkLabel(self.tab_clicker, text="Durum: Hazır [F6]", text_color="#00cc66", font=("Arial", 13, "bold"))
        self.clicker_status.pack(pady=10)

    def setup_ads_tab(self):
        self.ad_top_frame = ctk.CTkFrame(self.tab_ads, fg_color="#14213d")
        self.ad_top_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(self.ad_top_frame, text="Kaç Saniyede Bir Gönderilsin?", text_color="#66b3ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        self.ad_interval_entry = ctk.CTkEntry(self.ad_top_frame)
        self.ad_interval_entry.insert(0, "10")
        self.ad_interval_entry.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(self.tab_ads, text="Sıralı Reklam Mesaj Kutuları", text_color="#66b3ff", font=("Arial", 12, "bold")).pack(anchor="w", padx=15, pady=(5, 0))

        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_ads, fg_color="#14213d", height=250)
        self.scroll_frame.pack(pady=5, padx=10, fill="x")

        self.message_boxes = []
        self.add_message_box("Örn: /clan Satılık elmaslar!")

        self.add_box_btn = ctk.CTkButton(self.tab_ads, text="+ Yeni Mesaj Kutusu Ekle", fg_color="#0066cc", hover_color="#004d99", command=lambda: self.add_message_box(""))
        self.add_box_btn.pack(pady=5, padx=10, fill="x")

        self.ad_toggle_btn = ctk.CTkButton(self.tab_ads, text="Reklam Makrosunu Başlat (F7)", fg_color="#28a745", hover_color="#218838", command=toggle_ads_macro)
        self.ad_toggle_btn.pack(pady=10, padx=10, fill="x")

        self.ad_status = ctk.CTkLabel(self.tab_ads, text="Reklam Durumu: Kapalı [F7]", text_color="#ff4d4d", font=("Arial", 13, "bold"))
        self.ad_status.pack(pady=5)

    def add_message_box(self, default_text=""):
        box_frame = ctk.CTkFrame(self.scroll_frame, fg_color="#1a2b4c")
        box_frame.pack(pady=5, padx=5, fill="x")

        lbl = ctk.CTkLabel(box_frame, text=f"Kutu #{len(self.message_boxes) + 1}", text_color="#a6c8ff")
        lbl.pack(anchor="w", padx=5, pady=(2, 0))

        entry = ctk.CTkEntry(box_frame, placeholder_text="Gönderilecek mesajı yazın...", width=360)
        if default_text:
            entry.insert(0, default_text)
        entry.pack(side="left", padx=5, pady=5)

        del_btn = ctk.CTkButton(box_frame, text="X", width=35, fg_color="#cc0000", hover_color="#990000", command=lambda: self.remove_message_box(box_frame, entry))
        del_btn.pack(side="right", padx=5, pady=5)

        self.message_boxes.append(entry)

    def remove_message_box(self, frame, entry):
        if len(self.message_boxes) > 1:
            self.message_boxes.remove(entry)
            frame.destroy()
        else:
            entry.delete(0, 'end')

    def update_cps_label(self, value):
        self.cps_label.configure(text=f"Tıklama Hızı (CPS): {int(value)}")

    def update_keybind(self, choice):
        self.selected_key = choice
        self.clicker_status.configure(text=f"Durum: Hazır [{choice.upper()}]")

    def save_settings(self):
        data = {
            "keybind": self.key_dropdown.get(),
            "mouse_button": self.mouse_var.get(),
            "mode": self.mode_var.get(),
            "cps": self.cps_slider.get(),
            "limit": self.limit_entry.get(),
            "ad_interval": self.ad_interval_entry.get(),
            "messages": [box.get() for box in self.message_boxes]
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Ayarlar kaydedilemedi:", e)

    def load_settings(self):
        if not os.path.exists(CONFIG_FILE):
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "keybind" in data:
                self.key_dropdown.set(data["keybind"])
                self.selected_key = data["keybind"]
                self.clicker_status.configure(text=f"Durum: Hazır [{data['keybind'].upper()}]")
            if "mouse_button" in data:
                self.mouse_var.set(data["mouse_button"])
            if "mode" in data:
                self.mode_var.set(data["mode"])
            if "cps" in data:
                self.cps_slider.set(data["cps"])
                self.cps_label.configure(text=f"Tıklama Hızı (CPS): {int(data['cps'])}")
            if "limit" in data:
                self.limit_entry.delete(0, 'end')
                self.limit_entry.insert(0, data["limit"])
            if "ad_interval" in data:
                self.ad_interval_entry.delete(0, 'end')
                self.ad_interval_entry.insert(0, data["ad_interval"])
            if "messages" in data and data["messages"]:
                for box in self.message_boxes:
                    box.master.destroy()
                self.message_boxes.clear()

                for msg in data["messages"]:
                    self.add_message_box(msg)
        except Exception as e:
            print("Ayarlar yüklenemedi:", e)

    def on_closing(self):
        self.save_settings()
        self.destroy()

def click_loop():
    global is_clicking
    click_count = 0
    try:
        limit = int(app.limit_entry.get())
    except ValueError:
        limit = 0

    while is_clicking:
        if limit > 0 and click_count >= limit:
            stop_clicker()
            break

        m_choice = app.mouse_var.get()
        btn = Button.left if m_choice == "Sol" else (Button.right if m_choice == "Sağ" else Button.middle)

        cps = app.cps_slider.get()
        time.sleep(1.0 / cps)
        mouse.click(btn, 1)
        click_count += 1

def start_clicker():
    global is_clicking
    if not is_clicking:
        is_clicking = True
        app.clicker_status.configure(text="Durum: ÇALIŞIYOR...", text_color="#00cc66")
        threading.Thread(target=click_loop, daemon=True).start()

def stop_clicker():
    global is_clicking
    if is_clicking:
        is_clicking = False
        app.clicker_status.configure(text=f"Durum: Durduruldu [{app.selected_key.upper()}]", text_color="#ff4d4d")

def toggle_clicker():
    global is_clicking
    if is_clicking:
        stop_clicker()
    else:
        start_clicker()

def ads_loop():
    global is_ad_running
    current_index = 0

    while is_ad_running:
        try:
            interval = float(app.ad_interval_entry.get())
        except ValueError:
            interval = 10.0

        texts = [box.get().strip() for box in app.message_boxes if box.get().strip()]

        if not texts:
            app.ad_status.configure(text="Hata: Hiç mesaj girilmedi!", text_color="#ff4d4d")
            time.sleep(2)
            continue

        current_text = texts[current_index % len(texts)]

        app.clipboard_clear()
        app.clipboard_append(current_text)
        app.update()
        time.sleep(0.2)

        mouse.click(Button.left, 1)
        time.sleep(0.3)

        keyboard.press('t')
        keyboard.release('t')
        time.sleep(0.4)

        keyboard.press(Key.ctrl)
        time.sleep(0.9)
        keyboard.press('v')
        keyboard.release('v')
        time.sleep(0.2)
        keyboard.release(Key.ctrl)
        time.sleep(0.4)

        keyboard.press(Key.enter)
        keyboard.release(Key.enter)

        current_index += 1

        elapsed = 0
        while elapsed < interval:
            if not is_ad_running:
                break
            time.sleep(0.1)
            elapsed += 0.1

def toggle_ads_macro():
    global is_ad_running
    is_ad_running = not is_ad_running
    if is_ad_running:
        app.ad_status.configure(text="Reklam Durumu: ÇALIŞIYOR (Sıralı)...", text_color="#00cc66")
        app.ad_toggle_btn.configure(text="Reklam Makrosunu Durdur", fg_color="#dc3545", hover_color="#c82333")
        threading.Thread(target=ads_loop, daemon=True).start()
    else:
        app.ad_status.configure(text="Reklam Durumu: Kapalı [F7]", text_color="#ff4d4d")
        app.ad_toggle_btn.configure(text="Reklam Makrosunu Başlat (F7)", fg_color="#28a745", hover_color="#218838")

def check_key_match(key, target_key):
    if hasattr(key, 'name') and key.name == target_key:
        return True
    if isinstance(key, KeyCode) and key.char == target_key:
        return True
    if target_key == "space" and key == Key.space:
        return True
    return False

def on_press(key):
    try:
        if check_key_match(key, app.selected_key):
            if app.mode_var.get() == "Toggle":
                toggle_clicker()
            elif app.mode_var.get() == "Hold":
                start_clicker()

        if hasattr(key, 'name') and key.name == 'f7':
            toggle_ads_macro()
    except AttributeError:
        pass

def on_release(key):
    try:
        if check_key_match(key, app.selected_key):
            if app.mode_var.get() == "Hold":
                stop_clicker()
    except AttributeError:
        pass

if __name__ == "__main__":
    app = AutoClickerApp()

    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()

    app.mainloop()
