
from kivy.uix.stacklayout import StackLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.app import App
from kivy.lang import Builder

Builder.load_file("./mlp/widgets/notifications/notifications.kv")


class Notification(ButtonBehavior, Label):

    def __init__(self, text, **kwargs):
        super(Notification, self).__init__(**kwargs)
        self.text = text

    def on_press(self):
        self.parent.remove_widget(self)


class NotificationsManager(StackLayout):

    def __init__(self, **kwargs):
        super(NotificationsManager, self).__init__(**kwargs)

    def notify(self, text):
        nw = Notification(text)
        self.add_widget(nw)
        Clock.schedule_once(lambda dt: self.denotify(nw), 5)

    def denotify(self, notification_widget):
        self.remove_widget(notification_widget)


class TestApp(App):

    def build(self):
        root = Builder.load_file("./notifications.kv")
        return root


if __name__ == '__main__':
    TestApp().run()
