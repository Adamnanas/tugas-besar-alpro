import os
import json
import re
import uuid
import hashlib
import sqlite3
from datetime import datetime, timedelta
import kivy
kivy.require('2.1.0')
from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.metrics import dp
from plyer import call
from kivy.storage.jsonstore import JsonStore
from kivy.utils import platform
from kivy.properties import StringProperty
import uuid

try:
    from plyer import gps
except ImportError:
    gps = None

class DeviceManager:
    def __init__(self):
        """
        Initialize device manager with storage
        """
        self.store = JsonStore('device_info.json')
        
    def get_device_id(self):
        """
        Generate or retrieve a unique device identifier using a combination of available system information
        """
        import platform as platform_lib
        
        def generate_device_hash():
            
            system_info = [
                platform_lib.system(),           
                platform_lib.machine(),        
                platform_lib.processor(),        
                str(os.getenv('USER', '')),    
                str(os.getenv('HOME', '')),     
            ]
            
            system_str = '|'.join(filter(None, system_info))
            return hashlib.sha256(system_str.encode('utf-8')).hexdigest()
            
        if not self.store.exists('device_id'):
            device_id = str(uuid.uuid4())
            self.store.put('device_id', value=device_id)
        else:
            device_id = self.store.get('device_id')['value']



    def save_user_session(self, user_data):
        """
        Save user session data securely
        """
        self.store.put('user_session', 
                      device_id=self.get_device_id(),
                      user_data=user_data,
                      is_logged_in=True)

    def clear_session(self):
        """
        Clear stored session data
        """
        if self.store.exists('user_session'):
            self.store.delete('user_session')

    def is_logged_in(self):
        """
        Check if there's an active session
        """
        return (self.store.exists('user_session') and 
                self.store.get('user_session')['is_logged_in'])

    def get_stored_user(self):
        """
        Get stored user data if available
        """
        if self.is_logged_in():
            return self.store.get('user_session')['user_data']
        return None

class SecurityUtils:
     
    @staticmethod
    def hash_password(password, salt=None):
        """
        Securely hash passwords using PBKDF2 with SHA-256
        """
        if not salt:
            salt = uuid.uuid4().hex
        
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('utf-8'), 
                                      100000)
        return f"{salt}${pwdhash.hex()}"

    @staticmethod
    def verify_password(stored_password, provided_password):
        """
        Verify a stored password against one provided by user
        """
        salt, pwdhash = stored_password.split('$')
        return SecurityUtils.hash_password(provided_password, salt) == stored_password

    @staticmethod
    def validate_password(password):
        """
        Validate password strength:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"

    @staticmethod
    def validate_phone_number(phone):
        """
        Validate phone number format
        Supports international and local formats
        """
        phone_regex = r'^(\+62|62|^0)(\d{9,12})$'
        return re.match(phone_regex, phone) is not None


    @staticmethod
    def get_device_hash(device_id, user_id):
        """
        Create a unique hash for device-user combination
        """
        combined = f"{device_id}{user_id}".encode('utf-8')
        return hashlib.sha256(combined).hexdigest()

class DatabaseManager:
    def register_user(self, phone, name, password, email=None):
        """
    Register a new user in the database.
    """

        try:
            hashed_password = SecurityUtils.hash_password(password)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (phone, name, password, email)
                    VALUES (?, ?, ?, ?)
                ''', (phone, name, hashed_password, email))
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False 
          
    def get_connection(self):
      """
       Create and return a connection to the SQLite database.
      """
      return sqlite3.connect(self.db_name)

    def __init__(self, db_name='emergency_app.db'):
        """
        Initialize database connection and create tables
        """
        self.db_name = db_name
        self.create_tables()
    def create_tables(self):
        """
         Create necessary tables with enhanced schema
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
           
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT,
                emergency_contact_1 TEXT,
                emergency_contact_2 TEXT,
                registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                login_attempts INTEGER DEFAULT 0,
                is_locked BOOLEAN DEFAULT 0,
                lock_time DATETIME
            )
            ''')

            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                author_id INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                image_path TEXT,
                status TEXT DEFAULT 'pending',
                FOREIGN KEY(author_id) REFERENCES users(id)
            )
            ''')

            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                emergency_type TEXT,
                location TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'initiated',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            ''')

            conn.commit()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                device_id TEXT NOT NULL,
                device_hash TEXT NOT NULL,
                last_access DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY(user_id) REFERENCES users(id),
                UNIQUE(user_id, device_id)
            )
            ''')
            conn.commit()
    def authenticate_user(self, phone, password):
        """
         Authenticate user with phone number and password.
         """
        with self.get_connection() as conn:
             cursor = conn.cursor()
             cursor.execute('SELECT password FROM users WHERE phone = ?', (phone,))
             result = cursor.fetchone()
        if result and SecurityUtils.verify_password(result[0], password):
            return True
        return False

    def register_device(self, user_id, device_id):
        """
        Register a device for automatic login
        """
        device_hash = SecurityUtils.get_device_hash(device_id, user_id)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                INSERT OR REPLACE INTO device_auth 
                (user_id, device_id, device_hash, last_access, is_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
                ''', (user_id, device_id, device_hash))
                conn.commit()
                return True
            except sqlite3.Error:
                return False
    

    def get_user_by_device(self, device_id):
        """
        Get user data if device is registered
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            SELECT u.id, u.phone, u.name, u.email, u.emergency_contact_1, 
                   u.emergency_contact_2
            FROM users u
            JOIN device_auth d ON u.id = d.user_id
            WHERE d.device_id = ? AND d.is_active = 1
            ''', (device_id,))
            result = cursor.fetchone()
            
            if result:
                return {
                    'id': result[0],
                    'phone': result[1],
                    'name': result[2],
                    'email': result[3],
                    'emergency_contact_1': result[4],
                    'emergency_contact_2': result[5]
                }
            return None

class BaseScreen(Screen):
    """
    Base screen with common utility methods
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device_manager = DeviceManager()
        self.db_manager = DatabaseManager()

    def check_auto_login(self):
        """
        Check if automatic login is possible
        """
        if self.device_manager.is_logged_in():
            return True
            
        device_id = self.device_manager.get_device_id()
        user_data = self.db_manager.get_user_by_device(device_id)
        
        if user_data:
            self.device_manager.save_user_session(user_data)
            return True
            
        return False
    
    def show_popup(self, title, message):
        """
        Display a popup with a title and message.
        """
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text=message))
        close_button = Button(text='Close', size_hint=(1, 0.2))
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_enter(self):
        """
        Called when screen is entered
        """
        if self.check_auto_login():
            self.manager.current = 'MainMenu'

class LandingScreen(BaseScreen):
    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.device_manager = device_manager

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        logo = Image(source="app_frs2/logoo.jpg", size_hint=(1, 0.3))
        layout.add_widget(logo)
        
        
        self.phone_input = TextInput(
            hint_text='Phone Number', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.phone_input)
        
       
        self.password_input = TextInput(
            hint_text='Password', 
            password=True,
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.password_input)
        
        login_button = Button(
            text='Login', 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.login
        )
        layout.add_widget(login_button)
        
       
        register_button = Button(
            text='Register', 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.go_to_register
        )
        layout.add_widget(register_button)
        
        self.add_widget(layout)
    
    def login(self, instance):
        phone = self.phone_input.text
        password = self.password_input.text
        
        if not phone or not password:
            self.show_popup('Error', 'Please fill in all fields')
            return
        
        if not SecurityUtils.validate_phone_number(phone):
            self.show_popup('Error', 'Invalid phone number')
            return
        
        if self.db_manager.authenticate_user(phone, password):
            self.manager.current = 'main_menu'
        else:
            self.show_popup('Login Failed', 'Invalid credentials')
    
    def go_to_register(self, instance):
        self.manager.current = 'register'

    def on_size(self, *args):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class RegisterScreen(BaseScreen):
    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.device_manager = device_manager
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        logo = Image(source="app_frs2/logoo.jpg", size_hint=(1, 0.3))
        layout.add_widget(logo)

        self.name_input = TextInput(
            hint_text='Full Name', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.name_input)
        
        
        self.phone_input = TextInput(
            hint_text='Phone Number', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.phone_input)
        
        
        self.email_input = TextInput(
            hint_text='Email (Optional)', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.email_input)
        
        
        self.password_input = TextInput(
            hint_text='Password', 
            password=True,
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.password_input)
        
        
        self.confirm_password_input = TextInput(
            hint_text='Confirm Password', 
            password=True,
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.confirm_password_input)
        
        
        register_button = Button(
            text='Register', 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.register
        )
        layout.add_widget(register_button)
        
        
        back_button = Button(
            text='Back to Login', 
            size_hint_y=None, 
            height=dp(50),
            background_color=(0, 0.8, 0.8, 1),
            on_press=self.go_back
        )
        layout.add_widget(back_button)
        
        self.add_widget(layout)
    
    def register(self, instance):
        name = self.name_input.text
        phone = self.phone_input.text
        email = self.email_input.text
        password = self.password_input.text
        confirm_password = self.confirm_password_input.text
        
        
        if not all([name, phone, password]):
            self.show_popup('Error', 'Please fill in required fields')
            return
        
        if not SecurityUtils.validate_phone_number(phone):
            self.show_popup('Error', 'Invalid phone number')
            return
        
        if password != confirm_password:
            self.show_popup('Error', 'Passwords do not match')
            return
        
        
        password_valid, message = SecurityUtils.validate_password(password)
        if not password_valid:
            self.show_popup('Weak Password', message)
            return
        
        
        if self.db_manager.register_user(phone, name, password, email):
            self.show_popup('Success', 'Registration Successful')
            self.manager.current = 'landing'
        else:
            self.show_popup('Error', 'Phone number already registered')
    
    def go_back(self, instance):
        self.manager.current = 'landing'

    def on_size(self, *args):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class MainMenuScreen(BaseScreen):
    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.device_manager = device_manager
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        label = Label(
            text="Make Your Choice",
                size_hint=(1, 0.4),
                bold=True,
                color=(0,0,0,1),
                font_size="24sp"
                )
        layout.add_widget(label)

        menu_items = [
            ('Emergency Services', self.go_emergency),
            ('News & Reports', self.go_news),
            ('Profile', self.go_profile),
            ('Logout', self.logout)
        ]
        
        for label, callback in menu_items:
            btn = Button(
                text=label, 
                size_hint_y=None, 
                height=dp(125),
                background_color=(1,1,1,1),
                color=(0,0,0,1),
                background_normal="",
                font_size="24sp",
                on_press=callback
            )
            layout.add_widget(btn)
        
        self.add_widget(layout)
    
    def go_emergency(self, instance):
        self.manager.current = 'emergency'
    
    def go_news(self, instance):
        self.manager.current = 'news'
    
    def go_profile(self, instance):
        self.manager.current = 'profile'
    
    def logout(self, instance):
        self.manager.current = 'landing'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class EmergencyScreen(BaseScreen):
    def __init__(self, db_manager, device_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.device_manager = device_manager
        
       
        layout = GridLayout(cols=1, padding=dp(20), spacing=dp(10))
        
        emergency_services = [
            ('Police', self.call_police),
            ('Fire Department', self.call_fire),
            ('Medical Emergency', self.call_medical),
            ]
        
        for label, callback in emergency_services:
            btn = Button(
                text=label, 
                size_hint_y=None,
                height=dp(165),
                background_color=(1,1,1,1),
                color=(0,0,0,1),
                background_normal="",
                on_press=callback
            )
            layout.add_widget(btn)
        
        flayout = FloatLayout(size_hint=(1, None), height=50)

        button_kembali = Button(
                        text="<--",
                        size_hint=(0.2, 0.8),
                        pos_hint={'x': 0.01, 'y': 0},
                        background_color=(0, 0.8, 0.8, 1),
                        background_normal="",color=(0,0,0,1),
                        on_press=self.go_back
                        )
        
        flayout.add_widget(button_kembali)
        layout.add_widget(flayout)
        self.add_widget(layout)
    
    def call_police(self, instance):
        try:
            call.makecall('110')  # Nomor polisi di Indonesia
        except Exception as e:
            self.show_popup('Error', f'Could not call police: {e}')

    def call_fire(self, instance):
        try:
            call.makecall('113')  # Nomor pemadam kebakaran di Indonesia
        except Exception as e:
            self.show_popup('Error', f'Could not call fire department: {e}')

    def call_medical(self, instance):
        try:
            call.makecall('119')  # Nomor pemadam kebakaran di Indonesia
        except Exception as e:
            self.show_popup('Error', f'Could not call medical emergency: {e}')
    
    def share_location(self, instance):
        
        if gps:
            try:
                
                gps.configure(on_location=self.on_location)
                gps.start()
            except Exception as e:
                self.show_popup('GPS Error', f'Could not get location: {str(e)}')
        else:
           
            self.show_popup('GPS Error', 'GPS not available')
    
    def on_location(self, **kwargs):
        
        location_str = f"Lat: {kwargs.get('lat', 'N/A')}, Lon: {kwargs.get('lon', 'N/A')}"
        self.show_popup('Location', location_str)
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class NewsScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.scroll_view = ScrollView()
        self.news_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.news_layout.bind(minimum_height=self.news_layout.setter('height'))

        self.scroll_view.add_widget(self.news_layout)
        layout.add_widget(self.scroll_view)

        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        view_news_btn = Button(text='View News',
                               background_color=(1,1,1,1),
                               color=(0,0,0,1),
                               background_normal="",
                               on_press=self.load_news
                               )
        
        add_news_btn = Button(text='Add News',
                              background_color=(1,1,1,1),
                              color=(0,0,0,1),
                              background_normal="",
                              on_press=self.go_add_news
                              )
        
        back_btn = Button(text='Back to Menu',
                          background_color=(1,1,1,1),
                          color=(0,0,0,1),
                          background_normal="",
                          on_press=self.go_back
                          )
        
        button_layout.add_widget(view_news_btn)
        button_layout.add_widget(add_news_btn)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    

    def load_news(self, instance):
        self.news_layout.clear_widgets()

        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT title, description, category, created_at, id FROM news  ORDER BY created_at DESC''')
            news_items = cursor.fetchall()

            if not news_items:
                no_news_label = Label(
                    text='No news available',
                    size_hint_y=None,
                    height=dp(50)
                )
                self.news_layout.add_widget(no_news_label)
            else:
                for item in news_items:
                    news_item = BoxLayout(
                        orientation='vertical',
                        size_hint_y=None,
                        height=dp(150),
                        padding=dp(10),
                        spacing=dp(10),
                    )

                    title_label = Label(
                        text=f'[b]{item[0]}[/b]',
                        markup=True,
                        size_hint_y=None,
                        height=dp(40)
                    )

                    news_item.add_widget(title_label)
                    news_item.bind(on_touch_down=lambda instance, touch, news_id=item[4]: 
                        self.on_news_click(instance, touch, news_id)
                    )
                    self.news_layout.add_widget(news_item)

    def on_news_click(self, instance, touch, news_id):
        if instance.collide_point(*touch.pos):
            self.show_news_details(news_id)

    def show_news_details(self, news_id):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT title, description, category, created_at FROM news WHERE id = ?''', (news_id,))
            news_item = cursor.fetchone()

            if news_item:
                content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
                title_label = Label(text=f'[b]{news_item[0]}[/b]', markup=True, size_hint_y=None, height=dp(40))
                desc_label = Label(text=news_item[1], size_hint_y=None, height=dp(200), text_size=(Window.width - dp(40), None))
                category_label = Label(text=f'Category: {news_item[2]}', size_hint_y=None, height=dp(30))
                date_label = Label(text=f'Created at: {news_item[3]}', size_hint_y=None, height=dp(30))

                content.add_widget(title_label)
                content.add_widget(desc_label)
                content.add_widget(category_label)
                content.add_widget(date_label)

                close_button = Button(text="Close", size_hint_y=None, height=dp(40))
                close_button.bind(on_press=lambda _: self.close_popup())
                content.add_widget(close_button)

                self.popup = Popup(title="News Details", content=content, size_hint=(0.8, 0.8))
                self.popup.open()

    def close_popup(self):
        if hasattr(self, 'popup') and self.popup:
            self.popup.dismiss()
    
    def go_add_news(self, instance):
       
        self.manager.current = 'add_news'
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'
        
       
        if not news_item:
            no_news_label = Label(
                text='No news available', 
                size_hint_y=None, 
                height=dp(50)
            )
            self.news_layout.add_widget(no_news_label)
        else:
            for title, description, category, created_at in news_item:
                news_item = BoxLayout(
                    orientation='vertical', 
                    size_hint_y=None, 
                    height=dp(100),
                    padding=dp(10),
                    spacing=dp(5)
                )
                
                title_label = Label(
                    text=f'[b]{title}[/b]', 
                    markup=True,
                    size_hint_y=None, 
                    height=dp(30)
                )
                
                desc_label = Label(
                    text=description, 
                    text_size=(Window.width - dp(40), None),
                    size_hint_y=None,
                    height=dp(50)
                )
                
                meta_label = Label(
                    text=f'Category: {category} | {created_at}', 
                    size_hint_y=None, 
                    height=dp(20),
                    font_size='12sp'
                )
                
                news_item.add_widget(title_label)
                news_item.add_widget(desc_label)
                news_item.add_widget(meta_label)
                
                self.news_layout.add_widget(news_item)
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class AddNewsScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        
        self.title_input = TextInput(
            hint_text='News Title', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.title_input)
        
       
        self.category_input = TextInput(
            hint_text='Category (Emergency/Local/National)', 
            multiline=False,
            size_hint_y=None, 
            height=dp(40)
        )
        layout.add_widget(self.category_input)
        
        
        self.description_input = TextInput(
            hint_text='News Description', 
            multiline=True,
            size_hint_y=None, 
            height=dp(100)
        )
        layout.add_widget(self.description_input)
        
        
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        submit_btn = Button(text='Submit News',
                            background_color=(1,1,1,1),
                            color=(0,0,0,1),
                            background_normal="",
                            on_press=self.submit_news
                            )
        
        back_btn = Button(text='Cancel', 
                          background_color=(1,1,1,1),
                          color=(0,0,0,1),
                          background_normal="",
                          on_press=self.go_back
                          )
        
        button_layout.add_widget(submit_btn)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        
        self.add_widget(layout)
    
    def submit_news(self, instance):
        title = self.title_input.text
        category = self.category_input.text
        description = self.description_input.text
        
        
        if not all([title, category, description]):
            self.show_popup('Error', 'Please fill in all fields')
            return
        
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                INSERT INTO news 
                (title, description, category, status, created_at) 
                VALUES (?, ?, ?, ?, ?)
                ''', (title, description, category, 'approved', datetime.now()))
                conn.commit()
            
            
            self.title_input.text = ''
            self.category_input.text = ''
            self.description_input.text = ''
            
            self.show_popup('Success', 'News submitted for review')
            self.manager.current = 'news'
        
        except Exception as e:
            self.show_popup('Error', f'Could not submit news: {str(e)}')
    
    def go_back(self, instance):
        self.manager.current = 'news'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class ProfileScreen(BaseScreen):
    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        self.edit_mode = False
        
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        self.profile_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        layout.add_widget(self.profile_layout)
        
        
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        
        self.edit_toggle_btn = Button(text='Edit Profile', 
                                      background_color=(1,1,1,1),
                                      color=(0,0,0,1),
                                      background_normal="",
                                      on_press=self.toggle_edit_mode
                                      )
        
        emergency_contacts_btn = Button(text='Emergency Contacts', 
                                        background_color=(1,1,1,1),
                                        color=(0,0,0,1),
                                        background_normal="",
                                        on_press=self.go_emergency_contacts
                                        )
        
        back_btn = Button(text='Back to Menu', 
                          background_color=(1,1,1,1),
                          color=(0,0,0,1),
                          background_normal="",
                          on_press=self.go_back
                          )
        
        button_layout.add_widget(self.edit_toggle_btn)
        button_layout.add_widget(emergency_contacts_btn)
        button_layout.add_widget(back_btn)
        
        layout.add_widget(button_layout)
        
        
        self.save_btn = Button(text='Save Changes', 
                               on_press=self.save_profile_changes,
                               size_hint_y=None, 
                               height=dp(50),
                               opacity=0,
                               background_color=(1,1,1,1),
                               color=(0,0,0,1),
                               background_normal="",
                               )
        layout.add_widget(self.save_btn)
        
        self.add_widget(layout)
        
        
        self.original_user_data = None
    
    def on_enter(self):
        self.load_profile()
    
    def load_profile(self):
        
        self.profile_layout.clear_widgets()
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT name, phone, email, registration_date
                FROM users
                WHERE phone = ?
                LIMIT 1
                ''', (self.manager.get_screen('landing').phone_input.text,))
                user = cursor.fetchone()
            
            if user:
                name, phone, email, reg_date = user
                
                self.original_user_data = {
                    'name': name,
                    'phone': phone,
                    'email': email or '',
                    'registration_date': reg_date
                }
                
                
                self.profile_widgets = [
                    self.create_profile_row('Name', name),
                    self.create_profile_row('Phone', phone),
                    self.create_profile_row('Email', email or 'Not provided'),
                    self.create_profile_row('Registered', reg_date)
                ]
                
                
                for widget in self.profile_widgets:
                    self.profile_layout.add_widget(widget)
            
            else:
                self.profile_layout.add_widget(
                    Label(text='Could not load profile', size_hint_y=None, height=dp(40))
                )
        
        except Exception as e:
            self.show_popup('Error', f'Could not load profile: {str(e)}')
    
    def create_profile_row(self, label, value):
        
        row_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(40))
        
        
        label_widget = Label(
            text=f'{label}:', 
            size_hint_x=0.3, 
            text_size=(None, None), 
            halign='left'
        )
        
        
        value_widget = Label(
            text=str(value), 
            size_hint_x=0.7,
            text_size=(None, None), 
            halign='left'
        )
        
        
        value_widget.original_text = str(value)
        value_widget.field_name = label.lower()
        
        row_layout.add_widget(label_widget)
        row_layout.add_widget(value_widget)
        
        return row_layout
    
    def toggle_edit_mode(self, instance):
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            
            self.edit_toggle_btn.text = 'Cancel Edit'
            self.save_btn.opacity = 1
            
            
            for row in self.profile_layout.children[:]:
                label_widget = row.children[0]
                value_widget = row.children[1]
                
                
                edit_input = TextInput(
                    text=value_widget.text, 
                    size_hint_x=0.7,
                    multiline=False
                )
                
                
                row.remove_widget(value_widget)
                row.add_widget(edit_input)
        
        else:
            
            self.edit_toggle_btn.text = 'Edit Profile'
            self.save_btn.opacity = 0
            
            
            self.load_profile()
    
    def save_profile_changes(self, instance):
        try:
            
            new_data = {}
            for row in self.profile_layout.children[:]:
                label = row.children[0].text.replace(':', '').lower()
                value_input = row.children[1]
                
               
                if isinstance(value_input, TextInput):
                    new_data[label] = value_input.text
            
            
            if not all(new_data.values()):
                self.show_popup('Validation Error', 'All fields must be filled')
                return
            
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                UPDATE users
                SET name = ?, email = ?
                WHERE phone = ?
                ''', (
                    new_data['name'], 
                    new_data['email'], 
                    self.original_user_data['phone']
                ))
                conn.commit()
            
            
            self.toggle_edit_mode(instance)
            self.show_popup('Success', 'Profile updated successfully')
        
        except Exception as e:
            self.show_popup('Error', f'Could not save profile: {str(e)}')
    
    def go_emergency_contacts(self, instance):
        self.manager.current = 'emergency_contacts'
    
    def go_back(self, instance):
        self.manager.current = 'main_menu'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class EmergencyContactsScreen(BaseScreen):
    def emergency_call():
        call.makecall("000")  

    def __init__(self, db_manager, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = db_manager
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        
        contact1_layout = BoxLayout(size_hint_y=None, height=dp(50))
        self.contact1_input = TextInput(
            hint_text='Emergency Contact 1 Phone', 
            multiline=False,
            size_hint_x=0.7
        )
        add_contact1_btn = Button(text='Save', 
                                  size_hint_x=0.3, 
                                  on_press=lambda x: self.save_contact(1),
                                  background_color=(1,1,1,1),
                                  color=(0,0,0,1),
                                  background_normal=""
                                  )
                                  
        contact1_layout.add_widget(self.contact1_input)
        contact1_layout.add_widget(add_contact1_btn)
        layout.add_widget(contact1_layout)
        
       
        contact2_layout = BoxLayout(size_hint_y=None, height=dp(50))
        self.contact2_input = TextInput(
            hint_text='Emergency Contact 2 Phone', 
            multiline=False,
            size_hint_x=0.7
            )
        add_contact2_btn = Button(
            text='Save', 
            size_hint_x=0.3, 
            on_press=lambda x: self.save_contact(2),
            background_color=(1,1,1,1),
            color=(0,0,0,1),
            background_normal=""
            )
        contact2_layout.add_widget(self.contact2_input)
        contact2_layout.add_widget(add_contact2_btn)
        layout.add_widget(contact2_layout)
        
        
        back_btn = Button(
            text='Back to Profile', 
            size_hint_y=None, 
            height=dp(50),
            background_color=(1,1,1,1),
            color=(0,0,0,1),
            background_normal="",
            on_press=self.go_back
            )
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_enter(self):
        
        self.load_contacts()
    
    def load_contacts(self):
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                SELECT emergency_contact_1, emergency_contact_2 
                FROM users 
                WHERE phone = ?
                ''', (self.manager.get_screen('landing').phone_input.text,))
                contacts = cursor.fetchone()
            
            if contacts:
                self.contact1_input.text = contacts[0] or ''
                self.contact2_input.text = contacts[1] or ''
        except Exception as e:
            self.show_popup('Error', f'Could not load contacts: {str(e)}')
    
    def save_contact(self, contact_number):
        phone = self.manager.get_screen('landing').phone_input.text
        contact = (self.contact1_input.text if contact_number == 1 
                   else self.contact2_input.text)
        
        
        if not SecurityUtils.validate_phone_number(contact):
            self.show_popup('Error', 'Invalid phone number')
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                if contact_number == 1:
                    cursor.execute('''
                    UPDATE users 
                    SET emergency_contact_1 = ? 
                    WHERE phone = ?
                    ''', (contact, phone))
                else:
                    cursor.execute('''
                    UPDATE users 
                    SET emergency_contact_2 = ? 
                    WHERE phone = ?
                    ''', (contact, phone))
                conn.commit()
            
            self.show_popup('Success', f'Emergency Contact {contact_number} saved')
        except Exception as e:
            self.show_popup('Error', f'Could not save contact: {str(e)}')
    
    def go_back(self, instance):
        self.manager.current = 'profile'

    def on_size(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

    def on_pos(self, *args):
        with self.canvas.before:
            Color(0, 0.8, 0.8, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)

class EmergencyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = DatabaseManager()
        self.device_manager = DeviceManager()

    def build(self):
        
        sm = ScreenManager()

        sm.add_widget(LandingScreen(self.db_manager, self.device_manager, name='landing'))
        sm.add_widget(RegisterScreen(self.db_manager, self.device_manager, name='register'))
        sm.add_widget(MainMenuScreen(self.db_manager, self.device_manager, name='main_menu'))
        sm.add_widget(EmergencyScreen(self.db_manager, self.device_manager, name='emergency'))
        sm.add_widget(NewsScreen(self.db_manager, name='news'))
        sm.add_widget(AddNewsScreen(self.db_manager, name='add_news'))
        sm.add_widget(ProfileScreen(self.db_manager, name='profile'))
        sm.add_widget(EmergencyContactsScreen(self.db_manager, name='emergency_contacts'))

        self.screen_manager = sm

        return sm

    def on_start(self):
        """
        Dipanggil setelah aplikasi mulai.
        Periksa apakah pengguna dapat login otomatis.
        """
        self.check_auto_login()

    def check_auto_login(self):
     try:
        if self.device_manager.is_logged_in():
            self.screen_manager.current = 'main_menu'
        else:
            device_id = self.device_manager.get_device_id()
            user_data = self.db_manager.get_user_by_device(device_id)

            if user_data:
                self.device_manager.save_user_session(user_data)
                self.screen_manager.current = 'main_menu'
            else:
                self.screen_manager.current = 'landing'
     except Exception as e:
        print(f"Error during auto-login: {e}")
        self.screen_manager.current = 'landing'

if __name__ == "__main__":
    EmergencyApp().run()   
