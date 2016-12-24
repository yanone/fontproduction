# -*- coding: utf-8 -*-

import sys, time
from ynlib.fonts.fonttoolsstuff import Font as FontToolsFont
from ynlib.colors import Color
from ynlib.system import Execute
from ynglib import *
from ynglib.generators.DrawbotPDF import PDF
from ynglib.fonts import OpenTypeFont
from ynlib.strings import FormattedDate


#####################################################################################################################################

black = Color(CMYK=[0, 0, 0, 100])
white = Color(CMYK=[0, 0, 0, 0])
rose = Color(RGB=[255, 105, 125])

regularPath = '/Users/yanone/Schriften/Font Produktion/Fonts/NonameSans-Regular.otf'
regular = OpenTypeFont(regularPath)

#####################################################################################################################################



def trackingPerLanguages():

	hi = 0
	hil = None

	_list = []

	for scriptName in supports.keys():
	#	print scriptName
		for languageName, languageUnicodes in supports[scriptName]:
			left, bottom, right, top = f.boundsByUnicodes(languageUnicodes)
			lhi = int((top - bottom) / 1000.0 * 100) + 1
			_list.append('%s (%s%%)' % (languageName, lhi))
			

			if lhi > hi:
				hi = lhi
				hil = languageName
			elif lhi == hi:
				hil += ', ' + languageName

		print scriptName + ' script: ' + ', '.join(_list)
	#print 'Highest', hi, '%', hil


def logo(canvas, textcolor, logocolor):
	canvas.Text(regular, text = 'Yanone Type', fontsize = 20, x = 36.157, y = 25.33, align = 'left', fillcolor = textcolor)
	canvas.Ellipse(20.452, 17.172, 12.1, 12.1, fillcolor = white)
	canvas.Text(regular, text = u'', fontsize = 52, x = 20, y = 29.5, align = 'left', fillcolor = logocolor)


def centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, y, areaWidth, text, maxHeight = None, verticalCenter = 'top'):

	textWidthInUnits = 0
	for s in text:
		textWidthInUnits += ftFont.glyph(s).width

	# subtract sirebearings
	LSB = ftFont.glyph(text[0]).bounds()[0]
	RSB = ftFont.glyph(text[-1]).width - ftFont.glyph(text[-1]).bounds()[2]
	textWidthInUnits -= LSB + RSB

	# Calculate Text Size
	textSize = areaWidth * canvas.mm / textWidthInUnits * 1000

	if maxHeight:
		textSize = maxHeight * canvas.mm / (abs(ftFont.TTFont['OS/2'].sTypoDescender) + abs(ftFont.TTFont['OS/2'].sTypoAscender)) * 1000


	# Subtract Side Bearing Difference from left origin
	left = -1 * (LSB - RSB) / textSize

	ratio = textSize / 1000.0

	height = 1000
	width = 210
	
	if verticalCenter == 'top':
		top = y - (1000 - ftFont.TTFont['OS/2'].sTypoAscender) * ratio / canvas.mm

	elif verticalCenter == 'middle':
		baseline = textSize / canvas.mm
		ascender = baseline - ftFont.TTFont['OS/2'].sTypoAscender * ratio / canvas.mm
		descender = baseline - ftFont.TTFont['OS/2'].sTypoDescender * ratio / canvas.mm

		top = y - (abs(descender) + abs(ascender)) / 2.0

	baseline = top + textSize / canvas.mm
	xHeight = baseline - ftFont.TTFont['OS/2'].sxHeight * ratio / canvas.mm
	capHeight = baseline - ftFont.TTFont['OS/2'].sCapHeight * ratio / canvas.mm
	ascender = baseline - ftFont.TTFont['OS/2'].sTypoAscender * ratio / canvas.mm
	descender = baseline - ftFont.TTFont['OS/2'].sTypoDescender * ratio / canvas.mm

	# Metrics
	canvas.Line(-2, baseline, 214, baseline, strokecolor = black)
	canvas.Line(-2, xHeight, 214, xHeight, strokecolor = black)
	canvas.Line(-2, capHeight, 214, capHeight, strokecolor = black)
	canvas.Line(-2, ascender, 214, ascender, strokecolor = black)
	canvas.Line(-2, descender, 214, descender, strokecolor = black)

	# Actual text
	canvas.TextArea(pdfFont, text = text, fontsize = textSize, x = left, y = top, width = width, height = height, align = 'center', fillcolor = white)

	return descender - ascender


def titlePage(canvas, ftFont, pdfFont):
	canvas.Rect(-2, -2, 214, 297+4, fillcolor = Color(CMYK=[0, 0, 0, 85]))
	canvas.Rect(-2, -2, 214, 47.5, fillcolor = rose)
	logo(canvas, black, black)



	canvas.Text(regular, text = ftFont.TTFont['name'].getName(4, 1, 0, 0), fontsize = 30, x = 20, y = 83.93, align = 'left', fillcolor = white)
	canvas.TextArea(regular, text = 'Samples and technical specifications\n%s, %s' % (ftFont.version(), FormattedDate(time.time())), fontsize = 16, lineheight = 19.2, x = 20, y = 89.4, width = 210-40, height = 100, align = 'left', fillcolor = white)

	centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 186, 210 - 40, 'hag', verticalCenter = 'middle')

	if ftFont.fontfilepath.endswith('.otf'):
		text = u'For the OpenType/CFF font:\n%s' % os.path.basename(ftFont.fontfilepath)
	else:
		text = u'For the TrueType font:\n%s' % os.path.basename(ftFont.fontfilepath)

	canvas.TextArea(regular, text = text, fontsize = 16, lineheight = 19.2, x = 20, y = 261, width = 210, height = 50, fillcolor = white)

def makePDF(fontPath, pdfPath):

	ftFont = FontToolsFont(fontPath)
	pdfFont = OpenTypeFont(fontPath)


	from ynlib.web import GetHTTP
	import json
	languageSupport = json.loads(GetHTTP('http://192.168.56.101/yanone/?page=calculateLanguagesForUnicodes&unicodes=%s' % ','.join(map(str, ftFont.unicodes()))))

	canvas = Canvas(210, 297, 'mm')


	titlePage(canvas, ftFont, pdfFont)



	canvas.Generate(PDF(pdfPath))



makePDF(sys.argv[1], sys.argv[2])