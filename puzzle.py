import random
import copy
import matplotlib.pyplot as plt
import numpy
import os

import statistics
from deap import base
from deap import creator
from deap import tools

from eval import eval_solution

CORNER_POS = [0, 15, 240, 255]
BORDER_POS = range(1, 15) + range(241, 255) + [16, 32, 48, 64, 80, 96, 112, 128, 144, 160, 176, 192, 208, 224,
                                                 31, 47, 63, 79, 95, 111, 127, 143, 159, 175, 191, 207, 223, 239]
INSIDE_POS = [x for x in range(0, 255) if x not in CORNER_POS and x not in BORDER_POS]

def create_subdir(s):
  try:
    os.mkdir(s)
  except Exception as e:
    print e


class HoldLine(object):

  def __init__(self, f, arr):
    self.content = f(arr)
  def __getitem__(self, item):
    return copy.copy(self.content[item])
  def __setitem__(self, key, value):
    self.content[key] = value
  def count(self, obj):
    return len([x for x in self.content if x == obj])


class Puzzle(object):
  """
  Represant the game. Contain a population of each and get One fitnessValue.
  """
  def generate_graph_values(self, ngen=0):  # , size_avgs):
    nrow = [0, None, -1.0, 1.0]
    #[-100, -75, -50, -25, 0, 25, 50, 75, 100]

    fitnesses = self.get_other_values()
    y = 0
    for x in fitnesses:
      plt.scatter(y, x, marker='.', c='c')
      y += 1
    plt.axis(nrow)
    plt.ylabel("weight")
    plt.xlabel("population")
    plt.gcf().set_size_inches(15, 5)
    plt.savefig("gen/%s/puzzles/p_%s/g_%s.png" % (self.pid, self.uid, ngen), bbox_inches='tight', dpi=100)
    plt.clf()
    plt.close()

  def writeLogbook(self):
    with open("gen/%s/puzzles/logbook_%s.txt" % (self.pid, self.uid), "w") as f:
      f.write(str(self.logbook))

  def give_random_pos(self, pos, line):
    r = []
    for x in range(0, len(pos)):
      rp =  random.randrange(0, len(pos))
      rl = random.randrange(0, len(line))
      r.append((pos.pop(rp),line.pop(rl)))
    return r

  def randomize_lines(self, lc, lb, li):
    """
      Trying to have an half randomize algorithm
    :return:
    """
    lc = self.give_random_pos(copy.copy(CORNER_POS), lc)
    lb = self.give_random_pos(copy.copy(BORDER_POS), lb)
    li = self.give_random_pos(copy.copy(INSIDE_POS), li)
    l = lc + lb + li
    f = lambda lst, index, c: lst[c][1] if lst[c][0] == index else f(lst, index, c + 1)
    for x in xrange(0, 256):
      yield f(l, x, 0)

  def gen_ind(self, arr):
    c = arr[self.create_index]
    self.create_index += 1
    return c

  def __init__(self, f):
    uid, lines, pid = f()
    self.uid = uid
    self.pid = pid
    create_subdir("gen/%s/puzzles/p_%s" % (self.pid, self.uid))
    self.toolbox = base.Toolbox()
    # Used by creator.Individual
    self.create_index = 0

    creator.create("WeightMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", HoldLine, weight=creator.WeightMax)

    #Should be Optimized to put corner at the corner etc...
    arr = [line for line in self.randomize_lines(*lines)]

    self.toolbox.register("individual", creator.Individual, self.gen_ind, arr) # , arr)
    self.toolbox.register("desk", tools.initRepeat, list, self.toolbox.individual)
    self.population = self.toolbox.desk(n=len(arr)) # numpy.array(arr, dtype=list, order="F")

    # toolbox.register("mate", tools.cxTwoPoint)
    # Using this muttation for now. May change for ourself.
    # self.toolbox.register("mutate", lambda x, **kwargs: x.mutate(**kwargs), indpb=0.4)
    # toolbox.register("select", tools.selTournament, tournsize=3)
    # self.toolbox.register("evaluate", lambda pop: pop.evaluate())

    #
    self.stats = tools.Statistics(key=lambda ind: ind.weight.value)
    self.stats.register("avg", statistics.mean)
    self.stats.register("std", numpy.std)
    self.stats.register("min", min)
    self.stats.register("max", max)
    self.stats.register("median", statistics.median)
    self.logbook = tools.Logbook()
    self.logbook.header = "generation", "fitness", "min", "avg", "max"
    self.record = None

  def __len__(self):
    return len(self.content)

  def __repr__(self):
    return repr(self.uid)

  def get_other_values(self):
    return self.values

  def evaluate(self, eval=0):
    self.values, n = eval_solution(self.population)
    for ind, v in zip(self.population, self.values):
      ind.weight.value = v
    self.record = self.stats.compile(self.population)
    self.logbook.record(eval=eval, population=self.population, **self.record)
    return n,

  def get_mins_weight(self, weight):
    """
      Take Random Min Weight
    :param n:
    :return:
    """
    bad_pop = [x for x in self.population if x.weight.value <= weight]
    bad_pop_inside = [ind for ind in bad_pop if ind.count(0) == 0]
    bad_pop_border = [ind for ind in bad_pop if ind.count(0) == 1]
    bad_pop_corner = [ind for ind in bad_pop if ind.count(0) == 2]
    return bad_pop_corner, bad_pop_border, bad_pop_inside

  def set_new_position(self, elems, pos):
    new_pop = copy.copy(self.population)
    for elem in elems:

      new_pop.pop(new_pop.index(elem))
    for elem in elems:
      c = random.randrange(0, len(pos))
      new_pop.insert(pos[c], elem)
      pos.pop(c)
    self.population = new_pop

  def select(self):
    """
      This fonction should select X Individual that have the worst weight/Fitness
      They should be selected to be reset at different position
    :return:
    """
    def func(bp):
      if len(bp) > 0:
        pos = [self.population.index(x) for x in bp]
        self.set_new_position(bp, pos)
      else:
        print "Not Enough population to interchange", bp
    weight = -0.50 if self.record['avg'] >= -0.75 else -0.75
    bpc, bpb, bpi = self.get_mins_weight(weight)
    func(bpc)
    func(bpb)
    func(bpi)

  def mutate(self, indpb=0.0):
    """
    Based on deap.tools.mutShuffleIndexes
      Adjusting it for our own process.


    deap.tools.mutShuffleIndexes Documentation:
    Shuffle the attributes of the input individual and return the mutant.
    The *individual* is expected to be a :term:`sequence`. The *indpb* argument is the
    probability of each attribute to be moved. Usually this mutation is applied on
    vector of indices.

    :param individual: Individual to be mutated.
    :param indpb: Independent probability for each attribute to be exchanged to
                 another position.
    :returns: A tuple of one individual.

    This function uses the :func:`~random.random` and :func:`~random.randint`
    functions from the python base :mod:`random` module.

    :return:
    """
    size = len(self.population)
    for i in xrange(size):
      if random.random() < indpb:
        swap_indx = random.randint(0, size - 2)
        if swap_indx >= i:
          swap_indx += 1
        self.population[i], self.population[swap_indx] = \
          self.population[swap_indx], self.population[i]

#def Test_Random(lst, index, c=0):
#  f = lambda lst, index, c: list[c][1] if lst[c][0] == index else f(lst, index, c + 1)