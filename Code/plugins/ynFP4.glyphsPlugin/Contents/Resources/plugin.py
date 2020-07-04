# encoding: utf-8


import os, sys

path = '/Users/yanone/Schriften/fontproduction.git/Code'

if not path in sys.path:
	sys.path.insert(0, path)

import ynFP4
print 'ynFP4 loaded.'


###


path = '/usr/local/lib/python3.7/site-packages/git.pth'
paths = open(path, 'r').readlines()
for path in paths:
	if not path in sys.path:
		sys.path.insert(0, path)
		print('loaded', path)
