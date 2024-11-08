from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup

class EmergencyApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Label judul aplikasi
        title_label = Label(text="Aplikasi Darurat", font_size=24, size_hint=(1, 0.2))
        layout.add_widget(title_label)

        # Tombol SOS besar
        sos_button = Button(text="SOS", font_size=32, background_color=(1, 0, 0, 1), size_hint=(1, 0.3))
        sos_button.bind(on_release=self.show_sos_alert)
        layout.add_widget(sos_button)

        # Tombol untuk kontak darurat
        contact_button = Button(text="Kontak Darurat", font_size=20, size_hint=(1, 0.2))
        contact_button.bind(on_release=self.show_contacts)
        layout.add_widget(contact_button)

        # Tombol untuk lokasi
        location_button = Button(text="Lokasi", font_size=20, size_hint=(1, 0.2))
        location_button.bind(on_release=self.show_location)
        layout.add_widget(location_button)

        # Tombol untuk informasi medis
        medical_info_button = Button(text="Info Medis", font_size=20, size_hint=(1, 0.2))
        medical_info_button.bind(on_release=self.show_medical_info)
        layout.add_widget(medical_info_button)

        return layout

    # Fungsi untuk menampilkan popup SOS
    def show_sos_alert(self, instance):
        popup = Popup(title="SOS Alert",
                      content=Label(text="Panggilan Darurat Dikirim!"),
                      size_hint=(0.7, 0.5))
        popup.open()

    # Fungsi untuk menampilkan popup kontak darurat
    def show_contacts(self, instance):
        contacts = "1. Keluarga: 0812xxxxxx\n2. Teman: 0857xxxxxx"
        popup = Popup(title="Kontak Darurat",
                      content=Label(text=contacts),
                      size_hint=(0.7, 0.5))
        popup.open()

    # Fungsi untuk menampilkan popup lokasi
    def show_location(self, instance):
        popup = Popup(title="Lokasi Anda",
                      content=Label(text="Lokasi: Jl. Contoh, Kota ABC"),
                      size_hint=(0.7, 0.5))
        popup.open()

    # Fungsi untuk menampilkan popup informasi medis
    def show_medical_info(self, instance):
        medical_info = "Golongan Darah: A\nAlergi: Tidak Ada\nRiwayat: Hipertensi"
        popup = Popup(title="Info Medis",
                      content=Label(text=medical_info),
                      size_hint=(0.7, 0.5))
        popup.open()

# Menjalankan aplikasi
if __name__ == "__main__":
    EmergencyApp().run()