from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window


class MainApp(App):
    def build(self):
        Window.clear
        
        blayout = BoxLayout()
        blayout.orientation="vertical"
        label_judul = Label(text="Fast Respon Solution")

        button_darurat = Button(text="Darurat")
        button_darurat.size_hint=(0.5, 0.7)
        button_darurat.pos_hint={"center_x" : 0.5}


        button_jenis_berita = Button(text="Pilihan Jenis Berita",)
        button_jenis_berita.size_hint=(0.5, 0.7)
        button_jenis_berita.pos_hint={"center_x" : 0.5}

        blayout.add_widget(label_judul)
        blayout.add_widget(button_darurat)
        blayout.add_widget(button_jenis_berita)
        return blayout
    
MainApp().run()