import os
import pickle

import dill as dill

import ind
from puzzle import Puzzle

# WINDOWS TROUBLE ><
os.environ['TCL_LIBRARY'] = "C:\\Python27\\tcl\\tcl8.5"
os.environ['TK_LIBRARY'] = "C:\\Python27\\tcl\\tk8.5"

import config

def _load_file(s):
  try:
    with open(s, "r") as e:
      return dill.load(e)
  except Exception as e:
    print e
    return None

def load_population():

  f = _load_file(config.population_file_saved)
  if f != None: # Todo Save a basic population and reload it in the Puzzle
    print "Old Population Load First Check if ok remove the Raise and return f as e Puzzle"
    print type(f)
    print f
    raise NotImplemented

  # Loading a basic Population with a runner
  inds = ind.get_population()
  corner = [i for i in inds if i[1].count(0) == 2]
  border = [i for i in inds if i[1].count(0) == 1]
  inside = [i for i in inds if i[1].count(0) == 0]
  return Puzzle((corner, border, inside))


def save_population(puzzle):
  with open(config.population_file_saved, "w") as f:
    dill.dump(puzzle, f)
  print "Saved @%s" % config.population_file_saved

def loop(puzzle):
    """
      We Assume that the population is new an just setup and need to be eval first
    :param args:
    :param kwargs:
    :return:
    """
    for i in range(0, config.NGEN):
      # Evaluate the entire population
      puzzle.evaluate()
      # Example of call
      removed_tils = puzzle.select()
      # Example of call
      puzzle.crossover(removed_tils)
      # Example of call
      n_mutated = puzzle.mutate()
      # If you want log the different data
      puzzle.log_stats(i, n_mutated)
      # you may want to generate some graph
    print "Ended: ", config.NGEN, " generation\nWritting Stats file."
    # END LOOP
    # You may want to save the log book
    puzzle.write_stats()
    puzzle.draw_all_generations()
    # you may want to generate some graph
    print "Drawing avg for each generation"
    puzzle.generate_stats_generations(ftype="avg")
    print "Drawing min for each generation"
    puzzle.generate_stats_generations(ftype="min")
    print "Drawing max for each generation"
    puzzle.generate_stats_generations(ftype="max")
    print "Drawing Every Weight per Generations"
    puzzle.generate_graph_per_generations()
    # TODO implement
    save_population(puzzle)
    print "Ended Saving Data"

def main():
  try:
    os.mkdir("./gen/")
  except Exception as e:
    print e
  puzzle = load_population()
  loop(puzzle)


if __name__ == '__main__':
  main()
