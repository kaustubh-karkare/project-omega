"""A main function to trigger build automation"""
import sys
sys.path.append('../')
from build import Build
import os


build = Build(os.getcwd())
build.execute(sys.argv[1:])
