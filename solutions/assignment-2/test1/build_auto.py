"""Triggers build automation commands in the directory where this file exists"""
import sys
sys.path.append('../')
from build import Build
import os


build = Build(os.getcwd())
build.execute(sys.argv[1:])
