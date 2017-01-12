# -*- coding: utf-8 -*-

import sys, time, colorsys, random, cProfile, unicodedata
from ynlib.fonts.fonttoolsstuff import Font as FontToolsFont
from ynlib.colors import Color
from ynlib.system import Execute
from ynglib import *
from ynglib.generators.DrawbotPDF import PDF as DrawbotPDF
#from ynglib.generators.reportlabPDF import PDF as reportlabPDF
from ynglib.fonts import OpenTypeFont
from ynlib.strings import FormattedDate
from ynlib.maths import Interpolate
from ynlib.codepages import codepages


#####################################################################################################################################

black = Color(CMYK=[0, 0, 0, 100])
white = Color(CMYK=[0, 0, 0, 0])
rose = Color(RGB=[255, 105, 125])
grayBackground = Color(CMYK=[0, 0, 0, 10])

regularPath = '/Users/yanone/Schriften/Font Produktion/Fonts/NonameSans-Regular.otf'
regular = OpenTypeFont(regularPath)

PAGEMARGIN = 20
TEXTTOP = 60
TEXTSIZE = 10

#####################################################################################################################################


#  MAIN:



def makePDF(fontPath, pdfPath):

	ftFont = FontToolsFont(fontPath)
	pdfFont = OpenTypeFont(fontPath)


	from ynlib.web import GetHTTP
	import json
	
	startTime = time.time()
	languageSupport = json.loads(GetHTTP('http://192.168.56.101/yanone/?page=calculateLanguagesForUnicodes&unicodes=%s' % ','.join(map(str, ftFont.unicodes()))))
#	print 'http time: %ss' % (time.time() - startTime)
#	print languageSupport

	canvas = Canvas(210, 297, 'mm')


	titlePage(canvas, ftFont, pdfFont)

	languagesPage(canvas, languageSupport)

	codepagesPage(canvas, ftFont)

	trackingPage(canvas, ftFont, pdfFont, languageSupport)




	canvas.Generate(DrawbotPDF(pdfPath))

	Execute('gs -o "%s" -sDEVICE=pdfwrite -c "[ /PageMode /UseThumbs /View [/Fit] /PageLayout /SinglePage /DOCVIEW pdfmark"  -f "%s"' % (pdfPath.replace('.pdf', '_temp.pdf'), pdfPath))
	Execute('rm "%s"' % (pdfPath))
	Execute('mv "%s" "%s"' % (pdfPath.replace('.pdf', '_temp.pdf'), pdfPath))


#####################################################################################################################################


#  PAGES:


def titlePage(canvas, ftFont, pdfFont):
	canvas.Rect(-2, -2, 214, 297+4, fillcolor = Color(CMYK=[0, 0, 0, 85]))

	pageTitle(canvas, black, black, rose)



	canvas.Text(regular, text = ftFont.TTFont['name'].getName(4, 1, 0, 0), fontsize = 30, x = 20, y = 83.93, align = 'left', fillcolor = white)
#	canvas.Text(regular, text = '123\n1', fontsize = 30, x = 20, y = 83.93, align = 'right', fillcolor = white)
	canvas.TextArea(regular, text = 'Samples and technical specifications\n%s, %s' % (ftFont.version(), FormattedDate(time.time())), fontsize = 16, lineheight = 19.2, x = 20, y = 89.4, width = 210-40, height = 100, align = 'left', fillcolor = white)

	centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 186, 210 - 40, 'hag', verticalCenter = 'middle')

	if ftFont.fontfilepath.endswith('.otf'):
		text = u'For the OpenType/CFF font:\n%s' % os.path.basename(ftFont.fontfilepath)
	else:
		text = u'For the TrueType font\n%s' % os.path.basename(ftFont.fontfilepath)

	canvas.TextArea(regular, text = text, fontsize = 16, lineheight = 19.2, x = 20, y = 261, width = 210, height = 50, fillcolor = white)


def languagesPage(canvas, languageSupport):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Language support')

	canvas.TextArea(regular, text = 'This font supports the below listed languages.\nIf your desired language is missing from the list, get in touch and we’ll see what we can do.', fontsize = TEXTSIZE, x = PAGEMARGIN, y = TEXTTOP, width = 210 - 2*PAGEMARGIN, height = 50, align = 'left', fillcolor = black)

	text = ''
	for script in languageSupport.keys():
		text += script + ' Script:\n'
		text += ', '.join([x[0] for x in languageSupport[script]]) + '\n\n'

	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = PAGEMARGIN, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)


def codepagesPage(canvas, ftFont):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Codepage support')

	canvas.TextArea(regular, text = 'This font supports the below listed codepages.\nIf your desired codepage is missing from the list, get in touch and we’ll see what we can do.', fontsize = TEXTSIZE, x = PAGEMARGIN, y = TEXTTOP, width = 210 - 2*PAGEMARGIN, height = 50, align = 'left', fillcolor = black)

	text = ''

	fontUnicodes = ftFont.unicodes()
	_codepages = codepages()
	for codepage in sorted(_codepages.keys()):

		if set(fontUnicodes) >= set(_codepages[codepage]):

			text += codepage.replace(' - EBCDIC', '') + '\n'
#			print codepage, 'supported'

		else:
			missing = set(_codepages[codepage]) - set(range(32)) - set(fontUnicodes)

			if len(missing) < 30:
				pass
#				print 'missing from', codepage, map(hex, missing)


	canvas.TextArea(regular, text = '\n'.join(text.split('\n')[:43]), fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = PAGEMARGIN, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)

	canvas.TextArea(regular, text = '\n'.join(text.split('\n')[43:]), fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = 105, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)




def trackingPage(canvas, ftFont, pdfFont, languageSupport):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Minimum tracking (line height)')

	canvas.TextArea(regular, text = 'As a typesetter you’re responsible for setting not just the font size, but also the tracking (line height) of a text. When the tracking is too tight, letters of adjacent lines might collide. You can prevent this by setting the tracking to a certain percentage of the font size as a minimum.\nHowever, since different languages contain letters with different sizes, this minimum setting is not identical across languages or font designs. Below you’ll find an accurately calculated list of languages and the respective minimum tracking for each language for this particular font.', fontsize = TEXTSIZE, x = PAGEMARGIN, y = TEXTTOP, width = 210 - 1.7*PAGEMARGIN, height = 50, align = 'left', fillcolor = black)


	highest, lowest, lineGap, textSize = centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 104, 210 - 4*PAGEMARGIN, u'Ärger mitten', mode = 'tracking', verticalCenter = 'top', lineColor = grayBackground)
	highest, lowest, lineGap, textSize = centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 104 + lowest - highest, 210 - 4*PAGEMARGIN, u'in Österreich', mode = 'tracking', verticalCenter = 'top', lineColor = grayBackground, highest = highest, lowest = lowest, lineGap = lineGap, textSize = textSize)

	trackingPerLanguage = trackingPerLanguages(ftFont, languageSupport)

	germanTracking = 0
	for languageName, tracking in trackingPerLanguage['Latin']:
		if languageName == 'German':
			germanTracking = tracking
			break


	text = u'''The minimum tracking is calculated by the ratio of the highest/lowest points for each language (b for bounding box) with the fonts’ standard line height of 1000 upm units (em).
In the above example for the German language, the ratio is b/em = %s%%. That’s the minimum tracking for lines to not collide for sure. So set your tracking to at least %s%% of the font size. For 20pt font size that’s %spt tracking.
Please bear in mind that these are technical specifications for minium tracking and in no way represent aesthetically pleasing values. You’re the typesetter after all.

These are the minumum tracking values per language:

''' % (germanTracking, germanTracking, 20*germanTracking/100.0)

#	text += unicode(trackingPerLanguages(ftFont, languageSupport))


	for script in trackingPerLanguage.keys():
		text += script + ' Script:\n'
		text += ', '.join(['%s (%s%%)' % (x[0], x[1]) for x in trackingPerLanguage[script]]) + '\n\n'

	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, x = PAGEMARGIN, y = lowest + 15, width = 210 - 1.7*PAGEMARGIN, height = 297 - 23 - lowest + 15, align = 'left', fillcolor = black)
	


#	text = ''
#	for script in languageSupport.keys():
#		text += script + ' Script:\n'
#		text += ', '.join([x[0] for x in languageSupport[script]]) + '\n\n'
#
#	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = PAGEMARGIN, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)



#####################################################################################################################################


#  WIDGETS:



def trackingPerLanguages(ftFont, supports):

	hi = 0
	hil = None

	text = ''

	_list = {}

	for scriptName in supports.keys():

		_list[scriptName] = []

		for languageName, languageUnicodes in supports[scriptName]:
			left, bottom, right, top = ftFont.boundsByUnicodes(languageUnicodes)
			lhi = int((top - bottom) / 1000.0 * 100) + 1
			_list[scriptName].append((languageName, lhi))
			

			if lhi > hi:
				hi = lhi
				hil = languageName
			elif lhi == hi:
				hil += ', ' + languageName

	return _list

def logotype(canvas, textcolor, logocolor):
	canvas.Text(regular, text = 'Yanone Type', fontsize = 20, x = 36.157, y = 25.33, align = 'left', fillcolor = textcolor)
	logo(canvas, logocolor)

def logo(canvas, logocolor, position = 20):
	canvas.Ellipse(position + .452, 17.172, 12.1, 12.1, fillcolor = white)
	canvas.Text(regular, text = u'', fontsize = 52, x = position, y = 29.5, align = 'left', fillcolor = logocolor)


def centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, y, areaWidth, text, maxHeight = None, mode = 'title', verticalCenter = 'top', lineColor = None, highest = None, lowest = None, lineGap = 0, textSize = None):

	returnValue = None

	textWidthInUnits = 0
	for s in text:

		textWidthInUnits += ftFont.glyph(ord(s)).width

	# subtract sirebearings
	LSB = ftFont.glyph(ord(text[0])).bounds()[0]
	RSB = ftFont.glyph(ord(text[-1])).width - ftFont.glyph(text[-1]).bounds()[2]
	textWidthInUnits -= LSB + RSB

	# Calculate Text Size
	if not textSize:
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
#		if highest and lowest:
#			top = top - ((lowest - highest) / ratio * canvas.mm) * ratio / canvas.mm

	elif verticalCenter == 'middle':
		baseline = textSize / canvas.mm
		ascender = baseline - ftFont.TTFont['OS/2'].sTypoAscender * ratio / canvas.mm
		descender = baseline - ftFont.TTFont['OS/2'].sTypoDescender * ratio / canvas.mm

		top = y - (abs(descender) + abs(ascender)) / 2.0

	baseline = top + textSize / canvas.mm + lineGap
	xHeight = baseline - ftFont.TTFont['OS/2'].sxHeight * ratio / canvas.mm + lineGap
	capHeight = baseline - ftFont.TTFont['OS/2'].sCapHeight * ratio / canvas.mm + lineGap
	ascender = baseline - ftFont.TTFont['OS/2'].sTypoAscender * ratio / canvas.mm + lineGap
	descender = baseline - ftFont.TTFont['OS/2'].sTypoDescender * ratio / canvas.mm + lineGap

	# Metrics
	def randomColor():
		return Color(RGB=[x * 255 for x in colorsys.hls_to_rgb(random.random(), .5, 1.0)])

	if mode == 'title':
		strokewidth = 5
		fillcolor = white
	elif mode == 'tracking':
		strokewidth = 5
		fillcolor = black


	if mode == 'title':
		canvas.Line(-2, baseline, 214, baseline, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, xHeight, 214, xHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, capHeight, 214, capHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, ascender, 214, ascender, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, descender, 214, descender, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)

		returnValue = [ascender, descender]

	elif mode == 'tracking':

		canvas.Line(-2, baseline, 214, baseline, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
#		canvas.Line(-2, xHeight, 214, xHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, capHeight, 214, capHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
#		canvas.Line(-2, ascender, 214, ascender, strokecolor = black, strokewidth = strokewidth)
#		canvas.Line(-2, descender, 214, descender, strokecolor = black, strokewidth = strokewidth)


		#left, bottom, right, top = ftFont.boundsByUnicodes([ord(x) for x in text])
		bounds = ftFont.boundsByUnicodes([ord(x) for x in text])
		
		if highest:
			hi = highest + (lowest - highest)
		else:
			hi = baseline - bounds[3] * ratio / canvas.mm
		if not highest:
			canvas.Line(-2, hi, 214, hi, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		if lowest:
			lo = lowest + (lowest - highest)
		else:
			lo = baseline - bounds[1] * ratio / canvas.mm
		canvas.Line(-2, lo, 214, lo, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)

		abstand = .4
		beschriftungsAbstand = (2, 1)

		canvas.Arrow(PAGEMARGIN, lo - abstand, PAGEMARGIN, hi + abstand, strokecolor = rose, strokewidth = 1, beginning = True, end = True)
		canvas.Text(regular, text = 'b', fontsize = TEXTSIZE, x = PAGEMARGIN + beschriftungsAbstand[0], y = Interpolate(hi, lo, .5) + beschriftungsAbstand[1], align = 'left', fillcolor = rose.darken(.2))

		canvas.Arrow(PAGEMARGIN*1.5, lo - abstand, PAGEMARGIN*1.5, capHeight + abstand, strokecolor = rose, strokewidth = 1, beginning = True, end = True)
		canvas.Text(regular, text = 'em', fontsize = TEXTSIZE, x = PAGEMARGIN*1.5 + beschriftungsAbstand[0], y = Interpolate(capHeight, lo, .5) + beschriftungsAbstand[1], align = 'left', fillcolor = rose.darken(.2))


		returnValue = [hi, lo, (lo - descender), textSize]

	if mode == 'title':
		y = top
	elif mode == 'tracking':
		if highest and lowest:
			y = top + lineGap
		else:
			y = top


	# Actual text
	canvas.TextArea(pdfFont, text = text, fontsize = textSize, x = left, y = y, width = width, height = height, align = 'center', fillcolor = fillcolor)

	return returnValue




def pageTitle(canvas, textcolor, logocolor, backgroundColor, headline = None):

	canvas.Rect(-2, -2, 214, 47.5, fillcolor = backgroundColor)
	if headline:
		canvas.Text(regular, text = headline, fontsize = 20, x = 20, y = 25.33, align = 'left', fillcolor = textcolor)
		logo(canvas, logocolor, 210 - PAGEMARGIN - 12)
	else:
		logotype(canvas, textcolor, logocolor)




#cProfile.runctx("makePDF(sys.argv[1], sys.argv[2])", locals(), globals())

makePDF(sys.argv[1], sys.argv[2])

#makePDF('/Users/yanone/Schriften/Font Produktion/Fonts/NonameSans-Regular.otf', '/Users/yanone/Desktop/NonameSans-Regular.pdf')

