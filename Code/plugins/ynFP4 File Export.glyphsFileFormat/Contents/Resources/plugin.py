# encoding: utf-8

###########################################################################################################
#
#
#	File Format Plugin
#	Implementation for exporting fonts through the Export dialog
#
#	Read the docs:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/File%20Format
#
#	For help on the use of Interface Builder:
#	https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################


from GlyphsApp.plugins import *
import cProfile


# Preference key names
# Part of the example. You may delete them
otfPref = 'de.yanone.YNFPExport.exportOTF'
ttfPref = 'de.yanone.YNFPExport.exportTTF'
ttfHintingPref = 'de.yanone.YNFPExport.exportTTFHinting'
makePDFs = 'de.yanone.YNFPExport.makePDFs'
releaseDev = 'de.yanone.YNFPExport.releaseDev'
releaseProd = 'de.yanone.YNFPExport.releaseProd'

import ynExport

class YNFPExport(FileFormatPlugin):
	
	# Definitions of IBOutlets
	
	# The NSView object from the User Interface. Keep this here!
	dialog = objc.IBOutlet()
	
	# Example variables.
	otfCheckBox = objc.IBOutlet()
	ttfCheckBox = objc.IBOutlet()
	ttfHintingCheckBox = objc.IBOutlet()
	makePDFsCheckBox = objc.IBOutlet()
	releaseDevCheckBox = objc.IBOutlet()
	releaseProdCheckBox = objc.IBOutlet()
	
	def settings(self):
		self.name = 'Yanone FP Export'
		self.icon = 'ExportIcon'
		self.toolbarPosition = 3
		
		# Load .nib dialog (with .extension)
		self.loadNib('IBdialog')
	
	def start(self):
		# Init user preferences if not existent and set default value
		if Glyphs.defaults[otfPref] == None:
			Glyphs.defaults[otfPref] = True
		if Glyphs.defaults[ttfPref] == None:
			Glyphs.defaults[ttfPref] = False
		if Glyphs.defaults[ttfHintingPref] == None:
			Glyphs.defaults[ttfHintingPref] = False
		if Glyphs.defaults[makePDFs] == None:
			Glyphs.defaults[makePDFs] = False
		if Glyphs.defaults[releaseDev] == None:
			Glyphs.defaults[releaseDev] = False
		if Glyphs.defaults[releaseProd] == None:
			Glyphs.defaults[releaseProd] = False
		
		# Set initial state of checkboxes according to user variables
		self.otfCheckBox.setState_(Glyphs.defaults[otfPref])
		self.ttfCheckBox.setState_(Glyphs.defaults[ttfPref])
		self.ttfHintingCheckBox.setState_(Glyphs.defaults[ttfHintingPref])
		self.makePDFsCheckBox.setState_(Glyphs.defaults[makePDFs])
		self.releaseDevCheckBox.setState_(Glyphs.defaults[releaseDev])
		self.releaseProdCheckBox.setState_(Glyphs.defaults[releaseProd])

	@objc.IBAction
	def setExportOTF_(self, sender):
		Glyphs.defaults[otfPref] = bool(sender.intValue())
		if bool(sender.intValue()):
			Glyphs.defaults[ttfHintingPref] = False
			self.ttfHintingCheckBox.setState_(Glyphs.defaults[ttfHintingPref])

	@objc.IBAction
	def setExportTTF_(self, sender):
		Glyphs.defaults[ttfPref] = bool(sender.intValue())
		if bool(sender.intValue()):
			Glyphs.defaults[ttfHintingPref] = False
			self.ttfHintingCheckBox.setState_(Glyphs.defaults[ttfHintingPref])

	@objc.IBAction
	def setExportTTFHinting_(self, sender):
		Glyphs.defaults[ttfHintingPref] = bool(sender.intValue())
		if bool(sender.intValue()):

			# Turn off release
			Glyphs.defaults[releaseDev] = False
			self.releaseDevCheckBox.setState_(Glyphs.defaults[releaseDev])
			Glyphs.defaults[releaseProd] = False
			self.releaseProdCheckBox.setState_(Glyphs.defaults[releaseProd])

			# Turn off TTF and OTF
			Glyphs.defaults[otfPref] = False
			self.otfCheckBox.setState_(Glyphs.defaults[otfPref])
			Glyphs.defaults[ttfPref] = False
			self.ttfCheckBox.setState_(Glyphs.defaults[ttfPref])

			# Turn off PDFs
			Glyphs.defaults[makePDFs] = False
			self.makePDFsCheckBox.setState_(Glyphs.defaults[makePDFs])

	@objc.IBAction
	def setMakePDFs_(self, sender):
		Glyphs.defaults[makePDFs] = bool(sender.intValue())

	@objc.IBAction
	def setExportReleaseDev_(self, sender):
		Glyphs.defaults[releaseDev] = bool(sender.intValue())

		if bool(sender.intValue()):

			# Turn off PROD
			Glyphs.defaults[releaseProd] = False
			self.releaseProdCheckBox.setState_(Glyphs.defaults[releaseProd])

			# Turn on TTF and OTF
			Glyphs.defaults[otfPref] = True
			Glyphs.defaults[ttfPref] = True
			self.otfCheckBox.setState_(Glyphs.defaults[otfPref])
			self.ttfCheckBox.setState_(Glyphs.defaults[ttfPref])

			# Turn off TTF hinting test
			Glyphs.defaults[ttfHintingPref] = False
			self.ttfHintingCheckBox.setState_(Glyphs.defaults[ttfHintingPref])

			# Turn on PDFs
			Glyphs.defaults[makePDFs] = True
			self.makePDFsCheckBox.setState_(Glyphs.defaults[makePDFs])

	@objc.IBAction
	def setExportReleaseProd_(self, sender):
		Glyphs.defaults[releaseProd] = bool(sender.intValue())

		if bool(sender.intValue()):

			# Turn off DEV
			Glyphs.defaults[releaseDev] = False
			self.releaseDevCheckBox.setState_(Glyphs.defaults[releaseDev])

			# Turn on TTF and OTF
			Glyphs.defaults[otfPref] = True
			Glyphs.defaults[ttfPref] = True
			self.otfCheckBox.setState_(Glyphs.defaults[otfPref])
			self.ttfCheckBox.setState_(Glyphs.defaults[ttfPref])

			# Turn off TTF hinting test
			Glyphs.defaults[ttfHintingPref] = False
			self.ttfHintingCheckBox.setState_(Glyphs.defaults[ttfHintingPref])

			# Turn on PDFs
			Glyphs.defaults[makePDFs] = True
			self.makePDFsCheckBox.setState_(Glyphs.defaults[makePDFs])

	def export(self, font):
		reload(ynExport)
		success, message = ynExport.export(font)
		#cProfile.runctx('success, message = ynExport.export(font)', globals(), locals())
		return success, message
	
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
