import time
import streamlit as st

class Pipeline():

     def __init__(self, dict=None) -> None:
          self.steps = []
          if dict is not None:
               self.datablock = dict
          else:
               self.datablock = {}

     def add_step(self, func, params={}):
          self.steps.append((func, params))

     def datablock_write(self, path, value):

          current = self.datablock

          for key in path[:-1]:
               current = current.setdefault(key, {})
          current[path[-1]] = value

     def run(self, verbose=False):
          if verbose:
               print("Running pipeline")

          start = time.time()
          
          for func, params in self.steps:
               self.datablock = func(self.datablock, **params)
          end = time.time()
          
          if verbose:
               print("Total time: {} ms".format(round((end - start) * 1000)))
          