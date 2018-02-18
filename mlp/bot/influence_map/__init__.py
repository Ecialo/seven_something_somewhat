import numpy as np

from .position_map import compute_position_map
from .threat_map import compute_threat_map
from .health_map import compute_health_map
from .ap_map import compute_ap_map
from .potential_map import compute_potential_map
from .turn_order_map import compute_turn_order_map


def compose_influence_tensor():
    """
    [ap_map, health_map, turn_order_map, position_map, threat_map, potential_map]
    """
    pass
