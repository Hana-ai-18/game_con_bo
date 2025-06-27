from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior
from screens.background import ParallaxWidget

class ImageButton(ButtonBehavior, Image):
    pass

class ShopScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.bg_parallax = ParallaxWidget()
        self.add_widget(self.bg_parallax)

        self.current_index = 0
        self.skin_items = []

        self.build_ui()
        Window.bind(size=self.update_bg)

    def update_bg(self, *args):
        if hasattr(self, 'bg_parallax'):
            self.bg_parallax.on_resize()

    def build_ui(self):
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Title
        title = Label(text='[b][size=32]🛒 Shop[/size][/b]', markup=True, size_hint=(1, 0.1))
        self.main_layout.add_widget(title)

        # Points display
        self.points_label = Label(text='', size_hint=(1, 0.05), halign='center', markup=True)
        self.main_layout.add_widget(self.points_label)

        # Skin preview area
        preview_container = BoxLayout(size_hint=(1, 0.65), orientation='vertical', spacing=10)

        # Navigation + Skin Image
        skin_nav_layout = BoxLayout(size_hint=(1, 0.85), spacing=10)
        self.left_btn = ImageButton(source="assets/images/buttons/left_button.png", size_hint=(None, None), size=(60, 60))
        self.left_btn.bind(on_press=self.prev_skin)

        self.skin_image = Image(size_hint=(1, 1), allow_stretch=True)
        self.skin_bg = BoxLayout(size_hint=(0.8, 1), padding=10)
        self.skin_bg.add_widget(self.skin_image)

        self.right_btn = ImageButton(source="assets/images/buttons/right_button.png", size_hint=(None, None), size=(60, 60))
        self.right_btn.bind(on_press=self.next_skin)

        skin_nav_layout.add_widget(self.left_btn)
        skin_nav_layout.add_widget(self.skin_bg)
        skin_nav_layout.add_widget(self.right_btn)

        # Price label below skin image (yellow background effect can be set via skin_bg)
        self.price_label = Label(text='', markup=True, size_hint=(1, 0.15), halign='center', valign='middle')
        self.price_label.bind(size=self.price_label.setter('text_size'))

        preview_container.add_widget(skin_nav_layout)
        preview_container.add_widget(self.price_label)

        self.main_layout.add_widget(preview_container)

        # Action button (buy/use/using)
        self.action_btn = ImageButton(size_hint=(None, None), size=(200, 80), allow_stretch=True)
        self.action_btn.bind(on_press=self.on_action_pressed)
        self.main_layout.add_widget(self.action_btn)

        # Back button
        back_btn = Button(text='← Back', size_hint=(1, 0.1))
        back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'main_menu'))
        self.main_layout.add_widget(back_btn)

        self.add_widget(self.main_layout)

    def on_enter(self):
        app = App.get_running_app()
        self.dm = app.data_manager
        self.skin_items = [item for item in self.dm.get_shop_items() if item['type'] == 'skin']
        self.current_index = 0
        self.refresh_skin_display()

    def prev_skin(self, *args):
        self.current_index = (self.current_index - 1) % len(self.skin_items)
        self.refresh_skin_display()

    def next_skin(self, *args):
        self.current_index = (self.current_index + 1) % len(self.skin_items)
        self.refresh_skin_display()

    def refresh_skin_display(self):
        item = self.skin_items[self.current_index]
        app = App.get_running_app()
        points = self.dm.get_total_points()
        purchased = self.dm.get_purchased_items()
        equipped = self.dm.get_equipped_skin()

        self.points_label.text = f'[b]Points: {points}[/b]'

        skin_path = f"assets/images/characters/{item['id']}.png"
        self.skin_image.source = skin_path

        # Yellow background price label
        self.price_label.text = f"[color=ffff00][b]{item['name']} - {item['cost']} pts[/b][/color]"

        if item['id'] not in purchased:
            self.action_btn.source = "assets/images/buttons/buy_button.png"
        elif item['id'] == equipped:
            self.action_btn.source = "assets/images/buttons/using_button.png"
        else:
            self.action_btn.source = "assets/images/buttons/use_button.png"

    def on_action_pressed(self, *args):
        item = self.skin_items[self.current_index]
        item_id = item['id']
        purchased = self.dm.get_purchased_items()
        equipped = self.dm.get_equipped_skin()
        app = App.get_running_app()

        if item_id not in purchased:
            if self.dm.purchase_item(item_id):
                app.sound_manager.play_sound('coin')
                self.dm.set_equipped_skin(item_id)
            else:
                self.show_popup("Not enough points!")
                return
        elif item_id != equipped:
            self.dm.set_equipped_skin(item_id)
            app.sound_manager.play_sound('equip')

        self.refresh_skin_display()

    def show_popup(self, message):
        popup = Popup(title='Shop',
                      content=Label(text=message),
                      size_hint=(None, None), size=(300, 200))
        popup.open()
