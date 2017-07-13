# -*- coding: utf-8 -*-

import os, urllib, copy
from GlyphsApp import *
from AppKit import NSDate

import ynlib.web
reload(ynlib.web)

from ynlib.web import GetHTTP, PostHTTP, PostFiles
from ynlib.system import Execute

otfPref = 'de.yanone.YNFPExport.exportOTF'
ttfPref = 'de.yanone.YNFPExport.exportTTF'
ttfHintingPref = 'de.yanone.YNFPExport.exportTTFHinting'
makePDFs = 'de.yanone.YNFPExport.makePDFs'
releaseDev = 'de.yanone.YNFPExport.releaseDev'
releaseProd = 'de.yanone.YNFPExport.releaseProd'

import ynFP4
reload(ynFP4)
import ynFP4.features
reload(ynFP4.features)
import ynFP4.hinting
reload(ynFP4.hinting)
import ynFP4.checksum
reload(ynFP4.checksum)

devServer = 'http://192.168.56.101/yanone/'
prodServer = 'https://yanone.de'
upload = []
hinting = []
APIkey = {
	'dev': 'BzU4zFKdXxi6mQ9MI7XP',
	'prod': '',
}

folder = '/Users/yanone/Schriften/Font Produktion/Fonts'
hintingFolder = '/Users/yanone/Public/Hinting Test'

def export(font):

	font = copy.copy(font)
#	font.disableUpdateInterface()

	Glyphs.clearLog()


	# General stuff
	font.customParameters['vendorID'] = 'YN'

	# Set version
	if Glyphs.defaults[releaseDev]:
		server = devServer + '?page=latestFamilyVersion&familyName=%s&APIkey=%s' % (urllib.quote_plus(font.familyName), APIkey['dev'])
		font.versionMajor = 1
		font.versionMinor = int(GetHTTP(server).strip())
	if Glyphs.defaults[releaseProd]:
		server = prodServer + '?page=latestFamilyVersion&familyName=%s&APIkey=%s' % (urllib.quote_plus(font.familyName), APIkey['prod'])
		font.versionMajor = 1
		font.versionMinor = int(GetHTTP(server).strip())
	ynFP4.features.makeFeatures(font)

	# Set date
	font.date = NSDate.date()

	# Set missing Unicodes to Private Use Area
	if Glyphs.defaults[ttfHintingPref]:
		font = ynFP4.hinting.prepareForTrueTypeHintingTest(font)

#	if Glyphs.defaults[ttfHintingPref]:
#		masters = font.masters
#		masters = [masters[1], masters[0], masters[2]]
#		font.masters = masters	

	count = 0
	for instance in font.instances:

		instance.setFont_(font)

		if instance.active:
			
			for typeString, pref in (
					('OTF', otfPref),
					('TTF', ttfPref),
					):
				if Glyphs.defaults[pref]:

					path = os.path.join(folder, font.familyName.replace(' ', '') + '-' + instance.name.replace(' ', '') + '.' + typeString.lower())
					success = instance.generate(typeString)
					if success == True:
						print 'Generated %s' % path
						ynFP4.checksum.makeCheckSum(path, additionalValues = {'originalGenerator': 'Glyphs %s/%s' % (Glyphs.versionString, Glyphs.buildNumber)})
						count += 1
					else:
						print success

					if Glyphs.defaults[releaseDev]:
						upload.append(['dev', path, font.familyName, instance.name])
					if Glyphs.defaults[releaseProd]:
						upload.append(['prod', path, font.familyName, instance.name])

					# PDFs

					if Glyphs.defaults[makePDFs]:
						if os.path.exists(path + '.pdf'):
							os.remove(path + '.pdf')
						python = Execute('which python')
						call = "%s /Users/yanone/Schriften/fontproduction.git/Code/Font\ PDFs/makeFontPDF.py %s %s" % (python, path.replace(' ', '\ '), (path + '.pdf').replace(' ', '\ '))
						print Execute(call)
						if os.path.exists(path + '.pdf'):
							if Glyphs.defaults[releaseDev]:
								upload.append(['dev', path + '.pdf', font.familyName, instance.name])
							if Glyphs.defaults[releaseProd]:
								upload.append(['prod', path + '.pdf', font.familyName, instance.name])
						else:
							return False, 'Problems creating PDF for %s' % (os.path.basename(path))


			# TTF Hinting
			if Glyphs.defaults[ttfHintingPref]:

				path = os.path.join(hintingFolder, 'fonts', font.familyName.replace(' ', '') + '-' + instance.name.replace(' ', '') + '.ttf')
				instance.generate('TTF', path, AutoHint = False)
				instance.generate('TTF', path.replace('.ttf', '.autohinted.ttf'), AutoHint = True)
				count += 1

				hinting.append(path)

	if upload:
		for destination, path, familyName, fontName in upload:
			
			r = PostFiles(devServer, {
				'page': 'uploadFont',
				'familyName': familyName,
				'fontName': fontName,
				'fileName': os.path.basename(path),
				'font': open(path, "rb"),
				'APIkey': APIkey[destination],
			})
			print 'Uploaded %s' % os.path.basename(path), r

	# Hinting HTML
	if hinting:
		ynFP4.hinting.makeHintingTestPage(font, hinting, os.path.join(hintingFolder, 'hinting.html'))

#	font.enableUpdateInterface()

	return True, '%s Fonts exportiert.' % count
