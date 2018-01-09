import logging
import os
from collections import deque
from random import randint

import blinker

from mlp.commands.command import Place
from .actions.action import SPEED
from .bind_widget import bind_widget
from .grid import Grid
from .protocol import *
from .replication_manager import (
    GameObjectRegistry,
    GameObject,
)
from .tools import dict_merge
from .player import Player
from .unit import (
    Unit,
    PLANNING,
    ACTION
)

LAST = -1

# logger = logging.getLogger(__name__)
# handler = logging.FileHandler(
#     './game_logs/apply_actions{}.log'.format("_server" if os.environ.get("IS_SERVER") else ""),
#     'w',
# )
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

summon = blinker.signal("summon")
revoke = blinker.signal("revoke")
trace = blinker.signal("trace")
commands = blinker.signal("commands")
game_over = blinker.signal("game_over")
next_phase = blinker.signal("next_phase")


@bind_widget("TurnOrderIndicator")
class TurnOrderManager(GameObject):

    load_priority = -2
    hooks = ['load']

    def __init__(self, id_=None):
        super().__init__(id_)
        self._current_turn_order = []
        summon.connect(self.append_unit)
        revoke.connect(self.remove_unit)

    def __iter__(self):
        return iter((x[-1] for x in reversed(self._current_turn_order[::])))

    @property
    def units(self):
        return self.registry.categories[Unit.__name__]

    @staticmethod
    def get_current_unit_initiative(unit):
        ini = unit.stats.initiative
        return (
            max((randint(0, 10) for _ in range(ini))),
            ini,
            unit,
        )

    # @on_summon_event.connect_via('Unit')
    def append_unit(self, _, unit, cell=None):
        print("ON SUMMON")
        print(unit)
        self._current_turn_order.append(
            (LAST, unit.stats.initiative, unit,)
        )
        self._current_turn_order = self._current_turn_order[::]

    # @on_revoke_event.connect_via('Unit')
    def remove_unit(self, _, unit, cell):
        i_2_del = None
        for i, o_u in enumerate(self._current_turn_order):
            if unit in o_u:
                i_2_del = i
                break
        self._current_turn_order.pop(i_2_del)
        self._current_turn_order = self._current_turn_order[::]

    def rearrange(self):
        cur_turn_order = [self.get_current_unit_initiative(x[-1]) for x in self._current_turn_order]
        self._current_turn_order = sorted(cur_turn_order, reverse=True)

    def dump(self):
        print("CURRENT TURN ORDER")
        # print(self._current_turn_order)
        msg = dict_merge(
            super().dump(),
            {'current_turn_order': self._current_turn_order},
        )
        print(msg)
        return msg
        # return {
        #     **super().dump(),
        #     'current_turn_order': list(enumerate((RefTag(u) for u in self)))
        # }

    def load(self, struct):
        print("LOAD TURN ORDER")
        print(struct)
        super().load(struct)
        self._current_turn_order = sorted([tuple(r) for r in struct['current_turn_order']])


@bind_widget('RemoteGame')
class Game:

    hooks = ['receive_message']

    def __init__(self, players=None, grid=None, turn_order_manager=None):
        self.registry = GameObjectRegistry()
        self.state = PLANNING
        self.action_log = []
        self.commands = []
        self.handlers = {
            (message_type.GAME, game_message.CALL): self.registry.remote_call,
            (message_type.GAME, game_message.UPDATE): self.registry.load,
            (message_type.GAME, game_message.ACTION_APPEND): self.append_action,
            (message_type.GAME, game_message.ACTION_REMOVE): self.remove_action,
            (message_type.GAME, game_message.COMMAND): self.envoke_commands,
            (message_type.GAME, game_message.READY): self.setup_and_run,
            (message_type.GAME, game_message.GAME_OVER): lambda winner: game_over.send(winner=winner),
        }
        self._grid = grid
        self._turn_order_manager = turn_order_manager
        self._players = players

        trace.connect(self.add_to_commands)
        summon.connect(self.on_summon)

        if players:
            self.switch_state()
            summon.send(None, unit=players[0].main_unit, cell=self._grid[0, 0])
            summon.send(None, unit=players[-1].main_unit, cell=self._grid[4, 4])
            self.switch_state()
        self.winner = None
        for unit in self.units:
            unit.clear_presumed()
            unit.update_position()

    @property
    def players(self):
        if self._players is None:
            return self.registry.categories[Player.__name__]
        else:
            return self._players

    @property
    def units(self):
        return self.registry.categories[Unit.__name__]

    def receive_message(self, struct):
        type_pair = tuple(struct['message_type'])
        self.handlers[type_pair](struct['payload'])

    def append_action(self, action_struct):
        action = action_struct['action']
        author = action_struct['author']
        if author == action.owner.stats.owner or author == "overlord":
            action.owner.append_action(action)
        self.clear_presumed()
        self.apply_actions()

    def remove_action(self, action_struct):
        unit = action_struct['unit']
        author = action_struct['author']
        if unit.stats.owner == author or author == "overlord":
            unit.remove_action(None)
        self.clear_presumed()
        self.update_position()

    @property
    def units(self):
        return self.registry.categories[Unit.__name__]

    @property
    def grid(self):
        if self._grid is None:
            for o in self.registry:
                if isinstance(o, Grid):
                    self._grid = o
                    break
        return self._grid

    @property
    def turn_order_manager(self):
        if self._turn_order_manager is None:
            for o in self.registry:
                if isinstance(o, TurnOrderManager):
                    self._turn_order_manager = o
                    break
        return self._turn_order_manager

    def setup_and_run(self, payload):
        for player in self.players:
            if player.name == payload['author']:
                player.is_ready = True
        self.run()

    def run(self):
        """
        1) Начинается ход
        2) Начинается фаза
        3) Чуваки действуют
        4) Заканчивается фаза
        5) Повторяется 2-4
        6) Заканчивается ход
        :return:
        """
        result = False
        self.switch_state()
        if all((player.is_ready for player in self.players)):
            anyone_not_pass = self.apply_actions(True)
            for unit in self.turn_order_manager:
                unit.current_action_bar.clear()
            # dead_players = {player for player in self.players if player.main_unit.stats.health <= 0}
            # alive_players = set(self.players) - dead_players
            # if len(alive_players) == 1:
            #     self.declare_winner(alive_players.pop())
            #     return

            # Проверка на окончание игры
            alive_players = list(filter(lambda player: player.is_alive, self.players))
            if len(alive_players) <= 1:
                game_over.send(winner=alive_players.pop().name)

            if not anyone_not_pass:
                self.action_log[-1].append("--------------")
                for unit in self.units:
                    unit.launch_triggers(["turn", "end"], unit, unit.context)
                self.turn_order_manager.rearrange()
                for unit in self.units:
                    unit.refill_action_points()
                    unit.launch_triggers(["turn", "start"], unit, unit.context)
            for player in self.players:
                player.is_ready = False
            result = True
            self.clear_presumed()
            next_phase.send()   # Тут высылается сигнал о том, что можно высылать клиентам обновление
        self.switch_state()
        return result

    def apply_actions(self, log=False):
        anyone_not_pass = False
        # logger.debug("START APPLING ACTIONS")
        for unit in self.units:
            unit.launch_triggers(["phase", "start"], unit, unit.context)
        if log:
            self.action_log.append([])
        for unit in self.turn_order_manager:
            # logger.debug("APPLY FAST FOR {} in state {}".format(unit, unit.state))
            # print(unit)
            unit_is_not_pass = unit.apply_actions(speed=SPEED.FAST)
            # for unit_ in self.units:
            #     logger.debug("{} real stats {}".format(unit_, unit_._stats))
            #     logger.debug("{} presumed stats {}".format(unit_, unit_._stats.presumed))
            if log:
                self.action_log[-1].extend(unit.action_log)
            unit.action_log.clear()
            anyone_not_pass = anyone_not_pass or unit_is_not_pass
        for unit in self.turn_order_manager:
            # logger.debug("APPLY NORMAL FOR {} in state {}".format(unit, unit.state))
            # print(unit)
            unit_is_not_pass = unit.apply_actions()
            # for unit_ in self.units:
            #     logger.debug("{} real stats {}".format(unit_, unit_._stats))
            #     logger.debug("{} presumed stats {}".format(unit_, unit_._stats.presumed))
            if log:
                self.action_log[-1].extend(unit.action_log)
            unit.action_log.clear()
            anyone_not_pass = anyone_not_pass or unit_is_not_pass
        for unit in self.turn_order_manager:
            # print(unit)
            # logger.debug("APPLY SLOW FOR {} in state {}".format(unit, unit.state))
            unit_is_not_pass = unit.apply_actions(speed=SPEED.SLOW)
            # for unit_ in self.units:
            #     logger.debug("{} real stats {}".format(unit_, unit_._stats))
            #     logger.debug("{} presumed stats {}".format(unit_, unit_._stats.presumed))
            if log:
                self.action_log[-1].extend(unit.action_log)
            unit.action_log.clear()
            anyone_not_pass = anyone_not_pass or unit_is_not_pass
        for unit in self.units:
            unit.launch_triggers(["phase", "end"], unit, unit.context)
        # for unit in self.units:
        #     logger.debug("{} real stats {}".format(unit, unit.stats.resources))
        return anyone_not_pass

    # @staticmethod
    # def declare_winner(player):
    #     game_over.send(None, player=player)

    def switch_state(self):
        self.state = int(not self.state)
        for unit in self.units:
            # logger.debug("{} OLD STATS {}".format(unit, unit.stats))
            unit.switch_state()
            # logger.debug("{} NEW STATS {}".format(unit, unit.stats))
            # unit.clear_presumed()

    def update_position(self):
        for unit in self.units:
            unit.update_position()

    def clear_presumed(self):
        for unit in self.units:
            unit.clear_presumed()
        # self._grid.undo()

    # @trace.connect
    def add_to_commands(self, _, command):
        # pass
        if self.state is ACTION:
            self.commands.append(command)

    # @summon.connect
    def on_summon(self, _, unit, cell):
        print("SUMMONED", unit)
        trace.send(command=Place(
            unit=unit,
            place=cell,
            old_place=None
        ))

    def envoke_commands(self, new_commands):
        print("ENVOKE COMMANDS")
        new_commands = deque(new_commands)
        print(new_commands)
        # print("ENVOKE COMMANDS")
        commands.send(commands=new_commands)
