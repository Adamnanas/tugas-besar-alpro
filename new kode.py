from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.core.window import Window


# Setting Default Window Size for Testing (Web/PC)
Window.size = (360, 640)  # Simulasi ukuran perangkat Android


# Landing Page
class LandingPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        blayout = BoxLayout(orientation="vertical", padding=20, spacing=15, size_hint=(1, 1))
        
        # Logo
        logo = Image(source="logo.png", size_hint=(1, 0.3))
        blayout.add_widget(logo)
        
        # Input fields
        input_phone = TextInput(hint_text="Nomor Telepon", size_hint=(1, 0.1))
        blayout.add_widget(input_phone)
        
        input_nama = TextInput(hint_text="Nama Pengguna", size_hint=(1, 0.1))
        blayout.add_widget(input_nama)
        
        input_password = TextInput(hint_text="Kata Sandi", password=True, size_hint=(1, 0.1))
        blayout.add_widget(input_password)
        
        input_repassword = TextInput(hint_text="Konfirmasi Kata Sandi", password=True, size_hint=(1, 0.1))
        blayout.add_widget(input_repassword)
        
        # Buttons
        button_daftar = Button(text="DAFTAR", size_hint=(1, 0.1), background_color=(0, 0.5, 1, 1))
        blayout.add_widget(button_daftar)
        
        button_daftar_nanti = Button(text="Daftar Nanti", size_hint=(1, 0.1))
        button_daftar_nanti.bind(on_press=self.skip_registration)
        blayout.add_widget(button_daftar_nanti)
        
        self.add_widget(blayout)

    def skip_registration(self, instance):
        self.manager.current = "main_screen"


# Main Screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        blayout = BoxLayout(orientation="vertical", padding=20, spacing=15, size_hint=(1, 1))
        
        label = Label(text="Terdaftar Sebagai Akun", size_hint=(1, 0.2))
        blayout.add_widget(label)
        
        # Buttons for Emergency and News
        button_darurat = Button(text="DARURAT", size_hint=(0.5, 0.3), pos_hint={"center_x": 0.5})
        button_darurat.bind(on_press=self.go_to_emergency)
        blayout.add_widget(button_darurat)
        
        button_berita = Button(text="BERITA", size_hint=(0.5, 0.3), pos_hint={"center_x": 0.5})
        button_berita.bind(on_press=self.go_to_news)
        blayout.add_widget(button_berita)
        
        self.add_widget(blayout)

    def go_to_emergency(self, instance):
        self.manager.current = "emergency_screen"

    def go_to_news(self, instance):
        self.manager.current = "news_screen"


# Emergency Screen
class EmergencyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        blayout = GridLayout(cols=1, padding=20, spacing=15, size_hint=(1, 1))
        
        # Buttons for Police and Firefighters
        button_polisi = Button(text="POLISI", size_hint=(1, 0.3), background_color=(0.1, 0.7, 0.1, 1))
        blayout.add_widget(button_polisi)
        
        button_damkar = Button(text="DAMKAR", size_hint=(1, 0.3), background_color=(1, 0.1, 0.1, 1))
        blayout.add_widget(button_damkar)
        
        # Back Button
        button_kembali = Button(text="Kembali", size_hint=(1, 0.2))
        button_kembali.bind(on_press=self.go_back)
        blayout.add_widget(button_kembali)
        
        self.add_widget(blayout)

    def go_back(self, instance):
        self.manager.current = "main_screen"


# News Screen
class NewsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        blayout = BoxLayout(orientation="vertical", padding=20, spacing=15, size_hint=(1, 1))
        
        # News Buttons
        button_melihat = Button(text="Melihat Berita", size_hint=(1, 0.3), background_color=(0.5, 0.5, 1, 1))
        blayout.add_widget(button_melihat)
        
        button_melaporkan = Button(text="Melaporkan Berita", size_hint=(1, 0.3), background_color=(1, 0.7, 0.2, 1))
        blayout.add_widget(button_melaporkan)
        
        # Back Button
        button_kembali = Button(text="Kembali", size_hint=(1, 0.2))
        button_kembali.bind(on_press=self.go_back)
        blayout.add_widget(button_kembali)
        
        self.add_widget(blayout)

    def go_back(self, instance):
        self.manager.current = "main_screen"


# Main App
class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LandingPage(name="landing_page"))
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(EmergencyScreen(name="emergency_screen"))
        sm.add_widget(NewsScreen(name="news_screen"))
        return sm


if __name__ == "__main__":
    MainApp().run()
