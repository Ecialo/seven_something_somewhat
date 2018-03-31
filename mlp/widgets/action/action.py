from kivy.app import App
from kivy.uix.image import Image
from kivy.properties import ObjectProperty
from kivy.uix.gridlayout import GridLayout
from kivy.core.image import Image as CoreImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder

from mlp.serialization import (
    remote_action_append,
    remote_action_remove,
    make_struct
)
from ..general.image_button.image_button import ImageButton
from ..cursor import CURSOR_TABLE

Builder.load_file('./mlp/widgets/action/action.kv')


class RemoveActionButton(ImageButton):

    def __init__(self, action, **kwargs):
        super().__init__(**kwargs)
        self.action = action
        self.on_release_source = action.make_widget().on_release_source
        self.on_press_source = action.make_widget().on_press_source
        self.source = self.on_release_source

    def on_press(self):
        super().on_press()
        self.parent.send_action(self.action)
        # self.parent.remove_widget(self)


class Action(ImageButton):

    on_press_source = None
    on_release_source = None
    select_result = ObjectProperty(allownone=True)

    def __init__(self, action, **kwargs):
        self.action = action
        super(Action, self).__init__(**kwargs)
        self.setup_context = None
        self.bind(select_result=self.on_select_result)
        # self.texture = texture_released
        # self.source = 'atlas://data/images/defaulttheme/checkbox_off'
        self.source = self.on_release_source

    def on_press(self):
        # self.source = 'atlas://data/images/defaulttheme/checkbox_on'
        super().on_press()
        # print("PRIIIIINT")
        if self.action.pre_check():
            self.setup()
        # self.parent.send_action(self.action)
        #     print(self.__class__.__name__, self.ids)
        # self.texture = texture_pressed

    # def on_release(self):
    #     # self.source = 'atlas://data/images/defaulttheme/checkbox_off'
    #     self.source = self.on_release_source
    #     # self.texture = texture_released

    def setup(self):
        # print("Start setup")
        setup_context = self.action.setup()
        try:
            cursor_data = next(setup_context)
        except StopIteration:
            # print("SEND")
            self.parent.send_action(self.action.copy())
            # print("SENDED")
            self.action.clear()
        else:
        # print(setup_context)
        # if setup_context is not None:
            self.setup_context = setup_context
            # cursor_data = next(setup_context)
            self.make_cursor(*cursor_data)
        # else:
        #     self.parent.send_action(self.action)
        #     self.action.clear()

    def on_select_result(self, _, select_result):
        if self.setup_context and select_result is not None:
            try:
                cursor_data = self.setup_context.send(select_result)
                self.make_cursor(*cursor_data)
            except StopIteration:
                # print("SEND")
                c_action = self.action.copy()
                # print("Copied")
                self.parent.send_action(c_action)
                # print("Sended")
                self.setup_context = None
                self.select_result = None
        elif self.setup_context and select_result is None:
            self.setup_context = None
            self.action.clear()
        # print("Done")

    def make_cursor(self, cursor_name, cursor_args=None, cursor_kwargs=None):
        cursor_cls = CURSOR_TABLE[cursor_name]
        cursor = cursor_cls(self.parent.game, self, *(cursor_args or tuple()), **(cursor_kwargs or dict()))
        self.parent.game.add_cursor(cursor)


class NewAction(Action):

    def __init__(self, action, **kwargs):
        self.on_press_source = action.widget['pressed_icon']
        self.on_release_source = action.widget['icon']
        super().__init__(action, **kwargs)


class ActionBar(GridLayout):

    def __init__(self, action_bar, **kwargs):
        self.action_bar = action_bar
        super().__init__(**kwargs)
        self.update_bar()

    def update_bar(self):
        self.clear_widgets()
        # print(self.action_bar.actions)
        for action in self.action_bar.actions:
            self.add_widget(action.make_widget())

    @property
    def game(self):
        return self.parent

    def send_action(self, action):
        # print("SEND ACTION CONTEXT")
        # print("parent", self.parent)
        msg_struct = remote_action_append(action)
        msg_struct[1]["author"] = action.owner.stats.owner
        struct = make_struct(*msg_struct)
        self.parent.receive_message(struct)

    def on_load(self, _):
        self.update_bar()

    def on_append_action(self, _):
        self.update_bar()

    def on_remove_action(self, _):
        self.update_bar()


class CurrentActionBar(GridLayout):

    def __init__(self, current_action_bar, **kwargs):
        self.current_action_bar = current_action_bar
        super().__init__(**kwargs)
        self.remove_action_widgets = []

    def on_append_action(self, action):
        # print('accept action', action)
        if self.current_action_bar.actions and self.current_action_bar.actions[-1] == action:
            self.remove_action_widgets.append(RemoveActionButton(action))
            self.add_widget(self.remove_action_widgets[-1])

    def on_remove_action(self, action_index):
        # w = self.remove_action_widgets.pop()
        # self.remove_widget(w)
        # for child in self.children:
        #     self.remove_widget(child)
        self.clear_widgets()

    def send_action(self, action):
        # print(action)
        msg_struct = remote_action_remove(action)
        msg_struct[1]["author"] = action.owner.stats.owner
        self.parent.receive_message(make_struct(*msg_struct))
        # self.parent.network_manager.send(remote_action_remove(action))

# if __name__ == '__main__':
#     class SampleApp(App):
#         def build(self):
#             return ActionBar()
#
#     SampleApp().run()