# coding: utf-8

from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
import kivy.properties as prop

# from core.predef import pycard_protocol as pp
DEL = b'|||'
Builder.load_file("./mlp/widgets/chat/chat_widget.kv")


class ChatWidget(BoxLayout):

    app = prop.ObjectProperty()
    hidden_widgets = []

    def __init__(self, app, **kwargs):
        super(ChatWidget, self).__init__(**kwargs)
        self.app = app

        self.ids.input_field.bind(on_text_validate=self.send_chat_message)
        self.toggle()

    def print_message(self, msg):
        """
        Выводит текст в чат.
        """

        self.ids.chatlog.text += msg + "\n"
        self.scroll_if_necessary()
        self.ids.input_field.focus = True

    def scroll_if_necessary(self):
        """
        Прокручивает чат, если в нижней части скрыто более 2 строк текста.
        Судя по наблюдениям за интерфейсом, каждая строка имеет высоту 1.5 * font_h.
        """

        hidden_h = self.ids.chatlog.height - self.ids.chatlog_view.height
        font_h = self.ids.chatlog.font_size
        near_the_bottom = (self.ids.chatlog_view.scroll_y * hidden_h < 3.0 * font_h)
        if near_the_bottom:
            self.ids.chatlog_view.scroll_y = 0

    def send_chat_message(self, textinput):
        """
        Отправляет сообщение в чат.
        """
        text = self.ids.input_field.text
        # if DEL in text:
        #     text = text.replace(DEL, b'')
        self.ids.input_field.text = ""
        if text:
            self.app.send_chat_message(text)

    @property
    def is_visible(self):
        return len(self.children) > 0

    def fold(self):
        if not self.is_visible:
            return
        self.hidden_widgets = reversed(list(self.children))
        self.clear_widgets()

    def unfold(self):
        if self.is_visible:
            return
        for w in self.hidden_widgets:
            self.add_widget(w)
        self.hidden_widgets = []

    def toggle(self):
        if self.is_visible:
            self.fold()
        else:
            self.unfold()

