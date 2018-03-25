import numpy as np

# TODO сделать форму сигнала привлекающего юнита Это постепенно слабеющий купол радиуса 4 силы от 0.1 до 0.01

def stamp_into(form, center, layout):
    pass


# TODO Допинать
def compute_potential_map(unit, grid):
    """
    Куда юниту "интересно" двигаться.
    Стоять на месте -- не интересно
    Идти к врагам -- немного интересно
    Бить врагов -- очень интересно
    Тупить у стен -- не очень интересно
    """
    potential_map = np.zeros(grid.size, dtype='float64')
    unit_player = unit.player
    unit_signal = unit.signal
    for cell in grid:
        obj = cell.object
        if obj and obj.player != unit_player:
            stamp_into(unit_signal, obj.pos, potential_map)

        elif obj and obj == unit:
            potential_map[unit.pos] += -0.5
