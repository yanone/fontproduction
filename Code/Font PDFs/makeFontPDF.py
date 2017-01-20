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
from ynlib.fonts.opentypenames import *


#####################################################################################################################################

black = Color(CMYK=[0, 0, 0, 100])
white = Color(CMYK=[0, 0, 0, 0])
rose = Color(RGB=[255, 105, 125])
grayBackground = Color(CMYK=[0, 0, 0, 10])
green = Color(hex='97BF0D')

regularPath = '/Users/yanone/Schriften/Font Produktion/Fonts/NonameSans-Regular.otf'
regular = OpenTypeFont(regularPath)

PAGEMARGIN = 20
TEXTTOP = 60
TEXTSIZE = 10

SPECIMENTEXT1 = u'''“¡ÆABCDEFGHIJKLMNOØŒPÞQRSẞTUVWXYZ!”
»¿æabcdefghijklmnoøœpþqrsßtuvwxyz?«
(0123)[456]{789} $€₺₹£¥ @&¶%§℮№'''
SPECIMENTEXT2 = u'''Four furious friends fought for the phone. Auf des Fleischhauers Schild war der Abstand zwischen „Käse“ und „und“ und „und“ und „Wurst“ zu klein geraten. Tři sta třicet tři stříbrných křepelek přeletělo přes tři sta třicet tři stříbrných střech. Keksijä keksi keksin, keksin keksittyään keksijä keksi keksin keksityksi keksinnöksi.'''

pageTitles = []

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

	featuresPage(canvas, ftFont, pdfFont)

	codepagesPage(canvas, ftFont)

	leadingPage(canvas, ftFont, pdfFont, languageSupport)

	specimenPage(canvas, ftFont, pdfFont)

	contactPage(canvas, ftFont, pdfFont)

	canvas.Generate(DrawbotPDF(pdfPath))

	call = 'gs -o "%s" -sDEVICE=pdfwrite -c "%s [ /PageMode /UseOutlines /View [/Fit] /PageLayout /SinglePage /DOCVIEW pdfmark"  -f "%s"' % (pdfPath.replace('.pdf', '_temp.pdf'), (' '.join(["[ /Title (%s) /Page %s /OUT pdfmark" % (x[1], x[0]) for x in pageTitles])), pdfPath)
	Execute(call)
	Execute('rm "%s"' % (pdfPath))
	Execute('mv "%s" "%s"' % (pdfPath.replace('.pdf', '_temp.pdf'), pdfPath))


#####################################################################################################################################


#  PAGES:


def titlePage(canvas, ftFont, pdfFont):
	canvas.Rect(-2, -2, 214, 297+4, fillcolor = Color(CMYK=[0, 0, 0, 85]))

	pageTitle(canvas, black, black, rose)
	pageTitles.append([canvas.PageNumber(), 'Title page'])



	canvas.Text(regular, text = ftFont.TTFont['name'].getName(4, 1, 0, 0), fontsize = 30, x = 20, y = 83.93, align = 'left', fillcolor = white)
#	canvas.Text(regular, text = '123\n1', fontsize = 30, x = 20, y = 83.93, align = 'right', fillcolor = white)
	canvas.TextArea(regular, text = 'Samples and technical specifications\n%s, %s' % (ftFont.version(), FormattedDate(time.time())), fontsize = 16, lineheight = 19.2, x = 20, y = 89.4, width = 210-40, height = 100, align = 'left', fillcolor = white)

	centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 186, 210 - 40, 'hag', verticalCenter = 'middle')

	if ftFont.path.endswith('.otf'):
		text = u'For the OpenType/CFF font:\n%s' % os.path.basename(ftFont.path)
	else:
		text = u'For the TrueType font\n%s' % os.path.basename(ftFont.path)

	canvas.TextArea(regular, text = text, fontsize = 16, lineheight = 19.2, x = 20, y = 261, width = 210, height = 50, fillcolor = white)


def contactPage(canvas, ftFont, pdfFont):
	canvas.NewPage()

	pageTitles.append([canvas.PageNumber(), 'Contact'])

	canvas.Rect(-2, -2, 214, 297+4, fillcolor = Color(CMYK=[0, 0, 0, 85]))

	logo(canvas, rose, x = 99, y = 123)

	canvas.TextArea(regular, text = 'post@yanone.de\nhttps://yanone.de\nTwitter: @yanone', fontsize = 20, lineheight = 26, x = 0, y = 133, width = 210, height = 100, align = 'center', fillcolor = white)
	canvas.TextArea(regular, text = 'If you’ve designed something\nawesome with my fonts,\ndrop me a note!', fontsize = 10, lineheight = 13, x = 0, y = 215, width = 210, height = 100, align = 'center', fillcolor = white)


def languagesPage(canvas, languageSupport):
	canvas.NewPage()


	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Language support')
	pageTitles.append([canvas.PageNumber(), 'Language support'])

	canvas.TextArea(regular, text = 'This font supports the below listed languages.\nIf your desired language is missing from the list, get in touch and we’ll see what we can do.', fontsize = TEXTSIZE, x = PAGEMARGIN, y = TEXTTOP, width = 210 - 2*PAGEMARGIN, height = 50, align = 'left', fillcolor = black)

	text = ''
	for script in languageSupport.keys():
		text += script + ' Script:\n'
		text += ', '.join([x[0] for x in languageSupport[script]]) + '\n\n'

	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = PAGEMARGIN, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)


def codepagesPage(canvas, ftFont):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Codepage support')
	pageTitles.append([canvas.PageNumber(), 'Codepage support'])

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



def featuresPage(canvas, ftFont, pdfFont):

	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'OpenType layout features')
	pageTitles.append([canvas.PageNumber(), 'OpenType layout features'])

	coreTextSupportedFeatures = ['c2pc', 'c2sc', 'calt', 'case', 'cpsp', 'cswh', 'dlig', 'frac', 'liga', 'lnum', 'onum', 'ordn', 'pnum', 'rlig', 'sinf', 'smcp', 'ss01', 'ss02', 'ss03', 'ss04', 'ss05', 'ss06', 'ss07', 'ss08', 'ss09', 'ss10', 'ss11', 'ss12', 'ss13', 'ss14', 'ss15', 'ss16', 'ss17', 'ss18', 'ss19', 'ss20', 'subs', 'sups', 'swsh', 'titl', 'tnum']
	overwriteCoreTextSupportedFeatures = ['locl', 'zero', 'hist']
	excludeFeatures = ['']
	handledFeatures = []


	y = TEXTTOP
	maxCount = 6
	height = 20

	fontFeatures = ftFont.features()
	for feature in fontFeatures:
		if (feature in coreTextSupportedFeatures or feature in overwriteCoreTextSupportedFeatures) and not feature in excludeFeatures and not feature in handledFeatures:

			# See if this feature is a duplicate of another feature
			duplicate = None
			featureCompareString = ftFont.featureComparisonString(feature)
			for cf in fontFeatures:
				if cf != feature and ftFont.featureComparisonString(cf) == featureCompareString:
					duplicate = cf
					break

			# Name
			featureName = OTfeatures[feature]
			if duplicate:
				featureName += '\n' + '(also available as ' + OTfeatures[duplicate] + ')'
			canvas.TextArea(regular, text = featureName, fontsize = 12, x = PAGEMARGIN, y = y + 2, width = 210 - 2*PAGEMARGIN, height = 30, align = 'left', fillcolor = black)

			if feature in OTfeaturesOnByDefault:
				canvas.TextArea(regular, text = u'✓', fontsize = 16, x = PAGEMARGIN - 8, y = y+2, width = 210 - 2*PAGEMARGIN, height = 30, align = 'left', fillcolor = green)

			
			# Description
			description = []
			if OTfeatureDescriptions.has_key(feature):
				description.append(OTfeatureDescriptions[feature])
			if feature in OTfeaturesOnByDefault:
				description.append('Normally this feature should be active by default.')

			if description:
				canvas.TextArea(regular, text = '\n'.join(description), fontsize = 8, x = PAGEMARGIN, y = y + 8 + (5.5 if duplicate else 0), width = 75, height = 20, align = 'left', fillcolor = black.lighten(.5))

			sourceText = ''
			targetText = ''
			language = None

			sourceFeaturesOff = []
			sourceFeaturesOn = []
			targetFeaturesOff = []
			targetFeaturesOn = [feature]


			if feature == 'locl':
				if 'ROM' in ftFont.languages():
					language = 'ro'
					lookups = ftFont.lookupsPerFeatureScriptAndLanguage('locl', 'latn', 'ROM')
					for lookup in lookups:
						if lookup.Format == 1:
							for i, key in enumerate(lookup.mapping.keys()):
								if i <= maxCount and ftFont.glyph(key).unicode and ftFont.glyph(lookup.mapping[key]).unicode:
									sourceText += unichr(ftFont.glyph(key).unicode)
									targetText += unichr(ftFont.glyph(key).unicode)

			if feature == 'hist':
				lookups = ftFont.lookupsPerFeatureScriptAndLanguage('hist')
				for lookup in lookups:
					if lookup.Format == 1:
						for i, key in enumerate(lookup.mapping.keys()):
							if i <= maxCount and ftFont.glyph(key).unicode and ftFont.glyph(lookup.mapping[key]).unicode:
								sourceText += unichr(ftFont.glyph(key).unicode)
								targetText += unichr(ftFont.glyph(key).unicode)

			if feature == 'case':
				sourceText = u'–(A:B)'
				targetText = u'–(A:B)'

			if feature == 'frac':
				sourceText = '3 99/166'
				targetText = '3 99/166'

			if feature == 'sinf':
				sourceText = 'C20H25N3O'
				targetText = 'C20H25N3O'

			if feature == 'subs':
				sourceText = 'C20H25N3O'
				targetText = 'C20H25N3O'

			if feature == 'sinf':
				sourceText = 'C20H25N3O'
				targetText = 'C20H25N3O'

			if feature == 'sups':
				sourceText = '120m2'
				targetText = '120m2'

			if feature == 'ordn':
				sourceText = '1a 2o'
				targetText = '1a 2o'

			if feature == 'smcp':
				sourceText = 'abcdef'
				targetText = 'abcdef'

			if feature == 'c2sc':
				sourceText = 'ABCDEF'
				targetText = 'ABCDEF'

			if feature == 'lnum':
				sourceText = '0123456789'
				targetText = ''

			if feature == 'pnum':
				sourceText = '0123456789'
				targetText = ''

			if feature == 'onum':
				sourceText = '0123456789'
				targetText = ''

			if feature == 'tnum':
				sourceText = '0123456789'
				targetText = ''

			if feature == 'liga':
				sourceText = 'fi fl'
				targetText = 'fi fl'
				sourceFeaturesOff = ['liga']

			if feature == 'dlig':
				sourceText = 'ff tt'
				targetText = 'ff tt'

			if feature == 'zero':
				sourceText = '10'
				targetText = '10'

			canvas.TextArea(pdfFont, text = sourceText, fontsize = 24, x = 90, y = y, width = 50, height = 20, align = 'center', fillcolor = black, features = sourceFeaturesOn, featuresOff = sourceFeaturesOff)
			canvas.TextArea(regular, text = u'→',       fontsize = 20, x = 140, y = y + .8, width = 10, height = 10, align = 'center', fillcolor = rose)
			canvas.TextArea(pdfFont, text = targetText, fontsize = 24, x = 150, y = y, width = 50, height = 20, align = 'center', fillcolor = black, language = language, features = targetFeaturesOn, featuresOff = targetFeaturesOff)



			y += height
			handledFeatures.append(feature)
			if duplicate:
				handledFeatures.append(duplicate)

		if y > 297 - 25 - height:

			continueOnNextPage(canvas)
			canvas.NewPage()
			pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'OpenType layout features (continued)')
			pageTitles.append([canvas.PageNumber(), '...continued'])
			y = TEXTTOP


#	print ftFont.defaultNumerals()
#	print ftFont.glyphClasses()


def continueOnNextPage(canvas):
	canvas.TextArea(regular, text = u'continued on next page\n↓', fontsize = 14, x = 0, y = 274, width = 210, height = 20, align = 'center', fillcolor = rose)


def specimenPage(canvas, ftFont, pdfFont):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Type specimen')
	pageTitles.append([canvas.PageNumber(), 'Type specimen'])



	centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 79, 210 - 40, 'Hamburgefontsiv', verticalCenter = 'middle', lineColor = rose.lighten(.75), textColor = black, strokeWidth = 1.0)

	unicodes = ftFont.unicodes()

	for top, height, fontsize, lineheight in (
		(110.5, 40, 20, 24),
		(162.5, 32, 16, 19.2),
		(206, 20, 12, 14.4),
		(237, 16, 10, 12),
		(265, 11, 8, 9.6),
		):
		canvas.TextArea(pdfFont, text = SPECIMENTEXT2, fontsize = fontsize, lineheight = lineheight, x = PAGEMARGIN, y = top, width = 155, height = height + 5, align = 'left', fillcolor = black)
		canvas.TextArea(regular, text = '%s/%s pt' % (fontsize, lineheight), fontsize = 10, x = 180, y = top + 2 - top / 110.0, width = 20, height = 10, align = 'left', fillcolor = rose)


	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'All encoded glyphs')
	pageTitles.append([canvas.PageNumber(), 'All encoded glyphs'])


	text = u''
	t = []

#	for u in sorted(unicodes):
#		text += unichr(u)
#
#
#		if not unicodedata.category(unichr(u)) in t:
#			t.append(unicodedata.category(unichr(u)))
#
#	print t

	sorted_t = ['Lu', 'Ll', 'Nd', 'No', ['Sc', 'Cn'], 'P', 'Sm', ['Sk', 'Lm'], ['So', 'Co']]
	exclude_t = ['Cf', 'Zs', 'Mn']

	unicodesPrinted = []
	for cat in sorted_t:

#		text += str(cat) + ':\n'
		for u in sorted(unicodes):

			if type(cat) == str:
				if unicodedata.category(unichr(u)).startswith(cat):
					text += unichr(u)
					unicodesPrinted.append(u)

			elif type(cat) == list or type(cat) == tuple:
				if unicodedata.category(unichr(u)) in cat:
					text += unichr(u)
					unicodesPrinted.append(u)

		text += '\n'

	for u in sorted(unicodes):
		if not u in unicodesPrinted and not unicodedata.category(unichr(u)) in exclude_t:
			text += unichr(u)


	canvas.TextArea(regular, text = 'This page contains all glyphs of the font that have an assigned Unicode. There are more glyphs in the font that will only show as the result of applied OpenType layout features, such as Small Capitals, different numeral sets etc.\nPlease refer the »OpenType features« page for further information.', fontsize = 10, lineheight = 12, x = PAGEMARGIN, y = TEXTTOP, width = 170, height = 50, align = 'left', fillcolor = black)

	canvas.TextArea(pdfFont, text = text, fontsize = 18, lineheight = 23, x = PAGEMARGIN, y = TEXTTOP + 22, width = 170, height = 215 - 22, align = 'left', fillcolor = black)








def leadingPage(canvas, ftFont, pdfFont, languageSupport):
	canvas.NewPage()

	pageTitle(canvas, Color(CMYK=[0, 0, 0, 80]), rose, grayBackground, headline = 'Minimum leading (line height)')
	pageTitles.append([canvas.PageNumber(), 'Minimum leading'])

	canvas.TextArea(regular, text = 'As a typesetter you’re responsible for setting not just the font size, but also the leading (line height) of a text. When the leading is too tight, letters of adjacent lines might collide. You can prevent this by setting the leading to a certain percentage of the font size as a minimum.\nHowever, since different languages contain letters with different sizes, this minimum setting is not identical across languages or font designs. Below you’ll find an accurately calculated list of languages and the respective minimum leading for each language for this particular font.', fontsize = TEXTSIZE, x = PAGEMARGIN, y = TEXTTOP, width = 210 - 1.7*PAGEMARGIN, height = 50, align = 'left', fillcolor = black)


	highest, lowest, lineGap, textSize = centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 104, 210 - 4*PAGEMARGIN, u'Ärger mitten', mode = 'leading', verticalCenter = 'top', lineColor = grayBackground)
	highest, lowest, lineGap, textSize = centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, 104 + lowest - highest, 210 - 4*PAGEMARGIN, u'in Österreich', mode = 'leading', verticalCenter = 'top', lineColor = grayBackground, highest = highest, lowest = lowest, lineGap = lineGap, textSize = textSize)

	leadingPerLanguage = leadingPerLanguages(ftFont, languageSupport)

	germanTracking = 0
	for languageName, leading in leadingPerLanguage['Latin']:
		if languageName == 'German':
			germanTracking = leading
			break


	text = u'''The minimum leading is calculated by the ratio of the highest/lowest points for each language (b for bounding box) with the fonts’ standard line height of 1000 upm units (em).
In the above example for the German language, the ratio is b/em = %s%%. That’s the minimum leading for lines to not collide for sure. So set your leading to at least %s%% of the font size. For 20pt font size that’s %spt leading.
Please bear in mind that these are technical specifications for minium leading and in no way represent aesthetically pleasing values. You’re the typesetter after all.

These are the minimum leading values per language:

''' % (germanTracking, germanTracking, 20*germanTracking/100.0)

#	text += unicode(leadingPerLanguages(ftFont, languageSupport))


	for script in leadingPerLanguage.keys():
		text += script + ' Script:\n'
		text += ', '.join(['%s (%s%%)' % (x[0], x[1]) for x in leadingPerLanguage[script]]) + '\n\n'

	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, x = PAGEMARGIN, y = lowest + 15, width = 210 - 1.7*PAGEMARGIN, height = 297 - 23 - lowest + 15, align = 'left', fillcolor = black)
	


#	text = ''
#	for script in languageSupport.keys():
#		text += script + ' Script:\n'
#		text += ', '.join([x[0] for x in languageSupport[script]]) + '\n\n'
#
#	canvas.TextArea(regular, text = text, fontsize = TEXTSIZE, lineheight = TEXTSIZE * 1.3, x = PAGEMARGIN, y = 75, width = 210 - 2*PAGEMARGIN, height = 200, align = 'left', fillcolor = black)



#####################################################################################################################################


#  WIDGETS:



def leadingPerLanguages(ftFont, supports):

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

def logo(canvas, logocolor, x = 20, y = 29.5):
	canvas.Ellipse(x + .452, y - 12.1, 12.1, 12.1, fillcolor = white)
	canvas.Text(regular, text = u'', fontsize = 52, x = x, y = y, align = 'left', fillcolor = logocolor)


def centeredTypeSampleWithMetricsLines(canvas, ftFont, pdfFont, y, areaWidth, text, maxHeight = None, mode = 'title', verticalCenter = 'top', lineColor = None, highest = None, lowest = None, lineGap = 0, textSize = None, textColor = None, strokeWidth = None):

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
	elif mode == 'leading':
		strokewidth = 5
		fillcolor = black
	if textColor:
		fillcolor = textColor
	if strokeWidth:
		strokewidth = strokeWidth


	if mode == 'title':
		canvas.Line(-2, baseline, 214, baseline, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, xHeight, 214, xHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, capHeight, 214, capHeight, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, ascender, 214, ascender, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)
		canvas.Line(-2, descender, 214, descender, strokecolor = lineColor or randomColor(), strokewidth = strokewidth)

		returnValue = [ascender, descender]

	elif mode == 'leading':

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
		canvas.Text(regular, text = 'b', fontsize = TEXTSIZE, x = PAGEMARGIN + beschriftungsAbstand[0], y = Interpolate(hi, lo, .5) + beschriftungsAbstand[1], align = 'left', fillcolor = rose)

		canvas.Arrow(PAGEMARGIN*1.5, lo - abstand, PAGEMARGIN*1.5, capHeight + abstand, strokecolor = rose, strokewidth = 1, beginning = True, end = True)
		canvas.Text(regular, text = 'em', fontsize = TEXTSIZE, x = PAGEMARGIN*1.5 + beschriftungsAbstand[0], y = Interpolate(capHeight, lo, .5) + beschriftungsAbstand[1], align = 'left', fillcolor = rose)


		returnValue = [hi, lo, (lo - descender), textSize]

	if mode == 'title':
		y = top
	elif mode == 'leading':
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

