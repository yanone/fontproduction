from GlyphsApp import GSFont

featureOrder = ['aalt', 'ccmp', 'locl', 'subs', 'sinf', 'sups', 'numr', 'dnom', 'frac', 'ordn', 'lnum', 'pnum', 'tnum', 'onum', 'calt', 'hist', 'c2sc', 'smcp', 'case', 'isol', 'init', 'medi', 'fina', 'rlig', 'dlig', 'mkmk', 'liga', 'mgrk', 'zero', 'swsh', 'salt', 'ss01', 'ss02', 'ss03', 'ss04', 'ss05', 'ss06', 'ss07', 'ss08', 'ss09', 'ss10', 'ss11', 'ss12', 'ss13', 'ss14', 'ss15', 'ss16', 'ss18', 'ss19', 'ss20', 'ornm', 'ss17', 'cpsp', 'kern']
caseGlyphs = ["periodcentered", "bullet", "colon", "emdash", "endash", "hyphen", "guillemetleft", "guillemetright", "guilsinglleft", "guilsinglright", "plus", "minus", "multiply", "divide", "equal", "greater", "less", "backslash", "slash", "braceleft", "braceright", "bracketleft", "bracketright", "parenleft", "parenright", "dotmath", "notequal", "greaterequal", "lessequal", "plusminus", "approxequal", "asciitilde", "numbersign", "questiondown", "exclamdown", ]

UIReadySizeFeature = 'ss17'
UIReadyTop = 1040
UIReadyBottom = -260


def GSFont_UIReady(self):
	feature = UIReadySizeFeature
	top = UIReadyTop
	bottom = UIReadyBottom

	# Step 1: Find oversize glyphs
	oversize = []
	for glyph in self.glyphs:
		for layer in glyph.layers:
			if layer.bounds.origin.y < bottom or layer.bounds.origin.y + layer.bounds.size.height > top:
				oversize.append(glyph)

	# Step 2: Check for duplicates of oversize glyphs
	duplicates = []
	for glyph in oversize:
		if self.glyphs.has_key(glyph.name + '.' + feature):
			glyph = self.glyphs[glyph.name + '.' + feature]

			allLayersInBounds = True
			for layer in glyph.layers:
				if layer.bounds.origin.y < bottom and layer.bounds.origin.y + layer.bounds.size.height > top:
					allLayersInBounds = False
			if allLayersInBounds:
				duplicates.append(glyph)
		
	return len(oversize) == len(duplicates)

GSFont.UIReady = GSFont_UIReady