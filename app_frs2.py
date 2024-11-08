from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window

# Layar pertama: Halaman utama dengan tombol darurat dan berita
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Layout untuk layar utama
        blayout = BoxLayout()
        blayout.orientation="vertical"
        label_judul = Label(text="Fast Respon Solution")
        label_judul.size_hint=(1,0.2)
        label_judul.pos_hint={"center_x" : 0.5}
        
        # Tombol darurat
        button_darurat = Button(text="Darurat")
        button_darurat.size_hint=(0.5,0.3)
        button_darurat.pos_hint={"center_x" : 0.5}
        button_darurat.bind(on_press=self.click1)
        

        # Tombol jenis berita
        button_jenis_berita = Button(text="Pilihan Jenis Berita")
        button_jenis_berita.size_hint=(0.5,0.3)
        button_jenis_berita.pos_hint={"center_x" : 0.5}
        button_jenis_berita.bind(on_press=self.click2)
        
        

        # Menambahkan widget ke layout
        blayout.add_widget(label_judul)
        blayout.add_widget(button_darurat)
        blayout.add_widget(button_jenis_berita)
        

        # Menambahkan layout ke layar
        self.add_widget(blayout)

    def click1(self, instance):
        # Pindah ke layar "Panggilan Darurat"
        self.manager.current = "emergency_screen"

    def click2(self, instance):
        # Pindah ke layar "Pilihan Berita"
        self.manager.current = "news_screen"


# Layar kedua: Panggilan Darurat
class EmergencyScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        label = Label(text="Panggilan Darurat")
        label.size_hint=(1, 1)
        label.pos_hint={"center_x" : 0.5, "center_y": 0.5}
        self.add_widget(label)
        

# Layar ketiga: Pilihan Jenis Berita
class NewsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        label = Label(text="Pilihan Jenis Berita")
        label.size_hint=(1, 1)
        label.pos_hint={"center_x": 0.5, "center_y": 0.5}
        self.add_widget(label)


# Aplikasi utama
class MainApp(App):
    def build(self):
        # Membuat ScreenManager untuk mengelola beberapa layar
        sm = ScreenManager()

        # Menambahkan layar-layar yang ada
        sm.add_widget(MainScreen(name="main_screen"))
        sm.add_widget(EmergencyScreen(name="emergency_screen"))
        sm.add_widget(NewsScreen(name="news_screen"))

        return sm


# Menjalankan aplikasi
if __name__ == "__main__":
    MainApp().run()