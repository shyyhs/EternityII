"""
  Configuration:
    can be reloaded at runtime.
"""
import math

IMG="./Eternity/"

population_file_saved="try01.dill"

# population_file_base="test_4pieces.txt"
# population_file_base="test_9pieces.txt"
population_file_base="e2pieces.txt"

# NGEN % gen_modulo_elitism : 2000 / 100 = 20
# 20 * elitism_percentage_up : 20 * 4 = 80
# 80 + elitism_percentage_start : 80 + 10 = 90
# elitism_percentage_end = 90
NGEN = 2000
mutate_inpd=0.01
selection_ind_value_step=1
elitism_percentage_start=10
elitism_percentage_up=4
gen_modulo_elitism=100

# diff = connection_completions - score
select_light = 25.0
select_medium = 70.0
# select_heavy for other

# values dynamically computed with init()
initialized = False
size_line = 0
total = 0
corner_pos = []
border_bot_pos = []
border_top_pos = []
border_left_pos = []
border_right_pos = []
border_pos = []
inside_pos = []
score_group_max = 0

def count_nb_pieces():
    """
      Doc
    """
    nb_pieces = 0
    with open(population_file_base) as f:
        for i, line in enumerate(f):
            if line != "\n": nb_pieces += 1
    return nb_pieces

def deduce_line_size():
    """
      Doc
    """
    return int(round(math.sqrt(count_nb_pieces())))

def init():
    """
      Doc
    """
    globals()["size_line"] = deduce_line_size()
    globals()["total"] = size_line * size_line
    globals()["corner_pos"] = [0, size_line - 1, total - size_line, total - 1]
    globals()["border_bot_pos"] = range(corner_pos[2] + 1, corner_pos[3])
    globals()["border_top_pos"] = range(corner_pos[0] + 1, corner_pos[1])
    globals()["border_left_pos"] = range(corner_pos[1] + size_line, corner_pos[3], size_line)
    globals()["border_right_pos"] = range(corner_pos[0] + size_line, corner_pos[2], size_line)
    globals()["border_pos"] = border_top_pos + border_bot_pos  + border_left_pos + border_right_pos
    globals()["inside_pos"] = [x for x in range(0, total) if x not in corner_pos and x not in border_pos]
    globals()["score_group_max"] = 4 * total

if not initialized:
    init()
    globals()["initialized"] = True

__all__ = [ "init"
]
__md__ = [
    "init"
]
