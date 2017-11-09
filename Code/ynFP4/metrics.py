import math
	
def FontsBoundingBox(fonts, ignoreletters):

	font_lowest = None
	font_highest = None
	
	for f in fonts:
		for g in f.glyphs:
			if not g.name in ignoreletters:
				for l in g.layers:
			
					glyph_lowest = LowestPointOfGlyph(l)
					glyph_highest = HighestPointOfGlyph(l)
		
					if font_lowest == None or glyph_lowest < font_lowest:
						font_lowest = glyph_lowest

					if font_highest == None or glyph_highest > font_highest:
						font_highest = glyph_highest
	
	return int(font_lowest), int(font_highest)


def LowestPointOfGlyph(l):
	
	return l.bounds.origin.y

def HighestPointOfGlyph(l):
	return l.bounds.origin.y + l.bounds.size.height

def SetUnderline(f):

	hotglyph = None
	if f.glyphs.has_key('underline.comp'): hotglyph = 'underline.comp'
	elif f.glyphs.has_key('underscore'): hotglyph = 'underscore'

	if hotglyph:
		l = f.glyphs[hotglyph].layers[0]
		t = int(math.fabs(LowestPointOfGlyph(l) - HighestPointOfGlyph(l)))
		p = LowestPointOfGlyph(l) + (t / 2)
		f.instances[0].setCustomParameter_forKey_(int(p), 'underlinePosition')
		f.instances[0].setCustomParameter_forKey_(int(t), 'underlineThickness')

def SetStrikeout(f):
	
	hotglyph = None
	if f.glyphs.has_key('strikeout.comp'): hotglyph = 'strikeout.comp'
	elif f.glyphs.has_key('endash'): hotglyph = 'endash'

	if hotglyph:
		l = f.glyphs[hotglyph].layers[0]
		t = int(math.fabs(LowestPointOfGlyph(l) - HighestPointOfGlyph(l)))
		p = LowestPointOfGlyph(l) + (t / 2)
		f.instances[0].setCustomParameter_forKey_(int(p), 'strikeoutPosition')
		f.instances[0].setCustomParameter_forKey_(int(t), 'strikeoutThickness')

def SetVerticalMetrics(f, referencefonts, ignoreletters = []):

	
	# Get fonts' BBox
	lowestpoint, highestpoint = FontsBoundingBox(referencefonts, ignoreletters)
	
	# [hhea]
	hhea_ascender = highestpoint
	hhea_descender = lowestpoint
	hhea_line_gap = int( 1200 - math.fabs(hhea_ascender) - math.fabs(hhea_descender) )
	if hhea_line_gap < 10:
		hhea_line_gap = 10
	hhea_lineheight	= int( math.fabs(hhea_ascender) + math.fabs(hhea_descender) + hhea_line_gap )

	for instance in f.instances:
	
		instance.setCustomParameter_forKey_(hhea_ascender, 'hheaAscender')
		instance.setCustomParameter_forKey_(hhea_descender, 'hheaDescender')
		instance.setCustomParameter_forKey_(hhea_line_gap, 'hheaLineGap')
		
			
		# [OS/2]
		os2_typodescender = -250
		os2_typoascender = 750
		os2_typolinegap = int( hhea_lineheight - math.fabs(os2_typoascender) - math.fabs(os2_typodescender) )
		instance.setCustomParameter_forKey_(os2_typoascender, 'typoAscender')
		instance.setCustomParameter_forKey_(os2_typodescender, 'typoDescender')
		instance.setCustomParameter_forKey_(os2_typolinegap, 'typoLineGap')

		instance.setCustomParameter_forKey_(highestpoint, 'winAscent')
		instance.setCustomParameter_forKey_(lowestpoint, 'winDescent')
