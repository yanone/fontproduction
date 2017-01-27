# encoding: utf-8


import os, sys

path = '/Users/yanone/Schriften/fontproduction.git/Code'

if not path in sys.path:
	sys.path.insert(0, path)

import ynFP4
reload(ynFP4) 
print 'ynFP4 loaded.'