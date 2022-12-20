# encoding: utf-8

print("ynFP4 loadeding...")


import os, sys

path = "/Users/yanone/Schriften/fontproduction.git/Code"

if not path in sys.path:
    sys.path.insert(0, path)

import ynFP4

print("ynFP4 loaded.")


###

path = "/Users/yanone/Library/Application Support/Glyphs/GIT/GlyphsSDK/ObjectWrapper/GlyphsApp/"
sys.path.insert(0, path)
# print sys.path
# import GlyphsApp
# try:
# 	reload(GlyphsApp)
# except:
# 	pass
# try:
# 	reload(GlyphsApp)
# except:
# 	pass
# print('loaded', path)
# import GlyphsApp
print(GlyphsApp.__file__)


path = "/usr/local/lib/python3.9/site-packages/git.pth"
paths = open(path, "r").readlines()
for path in paths:
    if not path in sys.path:
        sys.path.insert(0, path)
        print("loaded", path)

path = "/usr/local/lib/python3.9/site-packages"
sys.path.append(path)
print("loaded", path)
