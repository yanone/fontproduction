# -*- coding: utf-8 -*-

import os, urllib
from GlyphsApp import *
from AppKit import NSDate

import ynlib.web
reload(ynlib.web)

from ynlib.web import GetHTTP, PostHTTP, PostFiles

otfPref = 'de.yanone.YNFPExport.exportOTF'
ttfPref = 'de.yanone.YNFPExport.exportTTF'
ttfHintingPref = 'de.yanone.YNFPExport.exportTTFHinting'
releaseDev = 'de.yanone.YNFPExport.releaseDev'
releaseProd = 'de.yanone.YNFPExport.releaseProd'

import ynFP4.features
reload(ynFP4.features)

devServer = 'http://192.168.56.101/yanone/'
prodServer = 'https://yanone.de'
upload = []
APIkey = {
	'dev': 'BzU4zFKdXxi6mQ9MI7XP',
	'prod': '',
}

def export(font):

#	Glyphs.clearLog()

	folder = '/Users/yanone/Schriften/Font Produktion/Fonts'
	hintingFolder = '/Users/yanone/Schriften/Font Produktion/Hinting Test/fonts'

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
		pass



	count = 0
	for instance in font.instances:



		if instance.active:
			



			if Glyphs.defaults[otfPref]:

				path = os.path.join(folder, font.familyName.replace(' ', '') + '-' + instance.name.replace(' ', '') + '.otf')
				instance.generate('OTF', path)
				count += 1

				if Glyphs.defaults[releaseDev]:
					upload.append(['dev', path, font.familyName, instance.name])
				if Glyphs.defaults[releaseProd]:
					upload.append(['prod', path, font.familyName, instance.name])

			if Glyphs.defaults[ttfPref]:

				path = os.path.join(folder, font.familyName.replace(' ', '') + '-' + instance.name.replace(' ', '') + '.ttf')
				instance.generate('TTF', path)
				count += 1

				if Glyphs.defaults[releaseDev]:
					upload.append(['dev', path, font.familyName, instance.name])
				if Glyphs.defaults[releaseProd]:
					upload.append(['prod', path, font.familyName, instance.name])

			if Glyphs.defaults[ttfHintingPref]:

				path = os.path.join(hintingFolder, font.familyName.replace(' ', '') + '-' + instance.name.replace(' ', '') + '.ttf')
				instance.generate('TTF', path)
				count += 1

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


	return True, '%s Fonts exportiert.' % count
