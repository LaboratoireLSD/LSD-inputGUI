__author__="gardnerthemaster"
__date__ ="$2009-09-15 09:47:58$"

from distutils.core import setup
from py2exe.build_exe import py2exe


setup (
  name = 'LSDGui',
  version = '0.1',
  windows=[{"script" : "Main.py"}], options={"py2exe" : {"includes" : ["sip", "PyQt4"]}}
)