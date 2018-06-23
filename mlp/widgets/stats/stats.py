import kivy.properties as prop
import kivy.uix.widget as widget
import kivy.uix.gridlayout as grl
from kivy.lang import Builder
from .resource import (
    NumericResource,
    StringResource,
    BooleanResource,
)
from kivy.uix.label import Label
Builder.load_file('./mlp/widgets/stats/stats.kv')


class Stats(grl.GridLayout):

    def __init__(self, stats, *args, **kwargs):
        super().__init__(**kwargs)
        self.stats = stats
        self.resources = {}
        self.add_widget(Label(text="Name: {}".format(stats.name)))
        self.add_widget(Label(text="Owner: {}".format(stats.owner)))
        for res_name, value in sorted(list(stats.resources.items())):
            resource = value.make_widget()
            # self.resources[res_name] = resource
            self.add_widget(resource)
        self.statuses = []

    def on_load(self, struct):
        for status_w in self.statuses:
            self.remove_widget(status_w)
        for status_name in struct['statuses']:
            self.statuses.append(Label(text=status_name))
            self.add_widget(self.statuses[-1])
        # for key in struct['resources']:
        #     self.resources[key].value = self.stats.resources[key]