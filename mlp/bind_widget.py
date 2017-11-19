# -*- coding: utf-8 -*-
import importlib
__author__ = 'ecialo'


def property_hook(method):

    event_name = "on_" + method.__name__

    def hooked(self, *args, **kwargs):
        method(self, *args, **kwargs)
        if (
                hasattr(self, "_widget")
                and hasattr(self._widget, event_name)
        ):
            self._widget.dispatch(event_name, *args, **kwargs)

    return hooked


def bind_widget(widget_name):

    def bind(component_cls):
        # Всё что ниже конченная жесть.
        # Я очень надеюсь, что мы придумаем что-нибудь поумнее для связи с виджетами.
        def make_widget(self, **kwargs):
            if not hasattr(self, '_widget') or not self._widget:
                try:
                    widget = getattr(importlib.import_module('mlp.widgets'), widget_name)
                except AttributeError:
                    raise AttributeError(msg="TAKOGO WIDGETA NEMA")    # TODO заменить на поиск по директории с игрой
                else:
                    self._widget = widget(self, **kwargs)
                    for method_name in component_cls.hooks:
                        self._widget.register_event_type("on_" + method_name)
            return self._widget

        component_cls.make_widget = make_widget
        for method_name in component_cls.hooks:
            setattr(
                component_cls,
                method_name,
                property_hook(getattr(
                    component_cls,
                    method_name
                ))
            )

        # ComponentWithWidget.__name__ = component_cls.__name__ + "WithWidget"

        return component_cls

    return bind



