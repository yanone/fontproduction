#!/usr/bin/python
# -*- coding: utf-8 -*-

import unicodedata, os, string
import dancingshoes.helpers
reload(dancingshoes.helpers)

import ynFP4
reload(ynFP4)
from dancingshoes import DancingShoes
from dancingshoes.helpers import GlyphNamesFromFontLabFont, GlyphNamesFromRoboFabFont, SubstitutionsFromCSV
from ynlib.fonts.opentypenames import OTfeatures


def makeFeatures(font):

	reload(ynFP4.features)
	import dancingshoes.helpers
	reload(dancingshoes.helpers)

	import copy
	from ynFP4.features import MakeDancingShoes
	from dancingshoes.helpers import GlyphNamesFromGlyphsFont

	print 'Dancing with my new shoes...'

	shoes = MakeDancingShoes(font, GlyphNamesFromGlyphsFont(font))

	# Apply code
	from dancingshoes.helpers import AssignFeatureCodeToGlyphsFont
	AssignFeatureCodeToGlyphsFont(font, shoes)

	# Glyphs' features
	onum = font.features['onum']
	font.updateFeatures()
	features = copy.copy(font.features)
	features.sort(key=lambda x: ynFP4.featureOrder.index(x.name))
	font.features = features
	if not onum:
		del(font.features['onum'])

	if shoes.Warnings():
		print shoes.Warnings()

	if shoes.Errors():
		print shoes.Errors()



def Unicode(g):
	u"""\
	Pull the hex Unicode value from various font object types.
	"""
	return g.unicode

# Dancing Shoes

def MakeDancingShoes(f, glyphnames, features = None, stylisticsetnames = None, defaultfigures = 'osf'):

	
	# Feature Duplication
	duplicateFeatures = [
		['hist', 'ss18'],
		['zero', 'ss19'],
		['salt', 'ss20'],
	]



	if not features:		
		features = ynFP4.featureOrder
	
	
	# Initialize DancingShoes object, hand over glyph names and default features
	shoes = DancingShoes(GlyphNamesFromFontLabFont(f), features)

	# Set stylistic set names
	if stylisticsetnames:
		for ssname in stylisticsetnames:
			shoes.SetStylisticSetName(ssname, stylisticsetnames[ssname])


	# UppercaseLetters
	for g in f.glyphs:
		if g.unicode and unicodedata.category == 'Lu':
			shoes.AddGlyphsToClass('@uppercaseLetters', g.name)

	# LowercaseLetters
	for g in f.glyphs:
		if g.unicode and unicodedata.category == 'Ll':
			shoes.AddGlyphsToClass('@lowercaseLetters', g.name)

	# Numbers
	shoes.AddGlyphsToClass('@numbers', ("zero","one","two","three","four","five","six","seven","eight","nine"))


	
	# Add direct substitutions
	directsubstitutions = (
		('smcp', '.sc'),
		('salt', '.salt'),
		('sups', '.sups'),
		('subs', '.subs'),
		('sinf', '.subs'),
		('swsh', '.swash'),
		('zero', '.zero'),


		)
	for feature, ending in directsubstitutions:
		shoes.AddSimpleSubstitutionFeature(feature, ending)
	
	# Add 
	for i in range(20):
		shoes.AddSimpleSubstitutionFeature('ss' + string.zfill(i + 1, 2), '.ss' + string.zfill(i + 1, 2))
	
	# Simple Substitutions from CSV file
	csvfiles = [
	os.path.join(os.path.dirname(__file__), 'substitutions.csv'),
	]
	for csvfile in csvfiles:
		for feature, source, target, script, language, lookup, lookupflag, comment in SubstitutionsFromCSV(csvfile):
			shoes.AddSubstitution(feature, source, target, script, language, lookupflag, comment, lookup)


	#LOCL
	for name in shoes.Glyphs():
		if '.locl_' in name:
			featureName, script, language = name.split('.')[1].split('_')
			shoes.AddSubstitution('locl', name.split('.')[0], name, script, language)


	#DLIG
	for name in shoes.Glyphs():
		if '_' in name:
			if not '.' in name or name.split('.')[1] == 'dlig':
				names = name.split('.')[0].split('_')
				if shoes.HasGlyphs(names):
					shoes.AddSubstitution('dlig', ' '.join(names), name)
				
	# Fraction feature
	if shoes.HasGroups(['.numr', '.dnom']) and shoes.HasGlyphs(['fraction']):
		shoes.AddSimpleSubstitutionFeature('numr', '.numr')
		shoes.AddSimpleSubstitutionFeature('dnom', '.dnom')
		
		shoes.AddGlyphsToClass('fractionslashes', ['slash', 'fraction'])
		shoes.AddSubstitution('frac', '@numr_source', '@numr_target')
		shoes.AddSubstitution('frac', 'slash', 'fraction')
		shoes.AddSubstitution('frac', "[@fractionslashes @dnom_target] @numr_target'", '@dnom_target')
	
	# ORDN
	if shoes.HasGlyphs(['a', 'a.sups', 'o', 'o.sups', "zero","one","two","three","four","five","six","seven","eight","nine"]):
#		shoes.AddGlyphsToClass('@ordn_source', 'a')
#		shoes.AddGlyphsToClass('@ordn_target', 'ordfeminine')
#		shoes.AddGlyphsToClass('@ordn_source', 'o')
#		shoes.AddGlyphsToClass('@ordn_target', 'ordmasculine')
		shoes.AddSubstitution('ordn', "[@numbers @ordn_target] @ordn_source'", '@ordn_target')

	for name in shoes.Glyphs():
		if name.endswith('.sups'):
			if unicodedata.category(unichr(int(f.glyphs[name.split('.')[0]].unicode, 16))) == 'Ll':
				shoes.AddGlyphsToClass('@ordn_source', name.split('.')[0])
				shoes.AddGlyphsToClass('@ordn_target', name)
	shoes.AddSimpleSubstitutionFeature('smcp', '.caps')

	
	
	# ZIFFERN
	
	if defaultfigures == 'osf':
	
		# lnum
		# one.tosf > one.tf
		for glyph in shoes.GlyphsInGroup('.tf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.tosf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@lnum_source', source)
				shoes.AddGlyphsToClass('@lnum_target', target)
		# one > one.lf
		for glyph in shoes.GlyphsInGroup('.lf'):
			source = shoes.SourceGlyphFromTarget(glyph)
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@lnum_source', source)
				shoes.AddGlyphsToClass('@lnum_target', target)
		if shoes.HasClasses(('@lnum_source', '@lnum_target')):
			shoes.AddSubstitution('lnum', "@lnum_source", '@lnum_target')
	
		# pnum
		# one.tf > one.lf
		for glyph in shoes.GlyphsInGroup('.lf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.tf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@pnum_source', source)
				shoes.AddGlyphsToClass('@pnum_target', target)
		if shoes.HasClasses(('@pnum_source', '@pnum_target')):
			shoes.AddSubstitution('pnum', "@pnum_source", '@pnum_target')
	
		# tnum
		# one.lf > one.tf
		for glyph in shoes.GlyphsInGroup('.tf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.lf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@tnum_source', source)
				shoes.AddGlyphsToClass('@tnum_target', target)
		# one > one.tosf
		for glyph in shoes.GlyphsInGroup('.tosf'):
			source = shoes.SourceGlyphFromTarget(glyph)
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@tnum_source', source)
				shoes.AddGlyphsToClass('@tnum_target', target)
		if shoes.HasClasses(('@tnum_source', '@tnum_target')):
			shoes.AddSubstitution('tnum', "@tnum_source", '@tnum_target')



	elif defaultfigures == 'lf':

		# onum
		# one > one.osf
		for glyph in shoes.GlyphsInGroup('.osf'):
			source = shoes.SourceGlyphFromTarget(glyph)
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@onum_source', source)
				shoes.AddGlyphsToClass('@onum_target', target)
		# one.tf > one.tosf
		for glyph in shoes.GlyphsInGroup('.tosf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.tf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@onum_source', source)
				shoes.AddGlyphsToClass('@onum_target', target)
		if shoes.HasClasses(('@onum_source', '@onum_target')):
			shoes.AddSubstitution('onum', "@onum_source", '@onum_target')

		# pnum
		# one.tosf > one.osf
		for glyph in shoes.GlyphsInGroup('.osf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.tosf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@pnum_source', source)
				shoes.AddGlyphsToClass('@pnum_target', target)
		if shoes.HasClasses(('@pnum_source', '@pnum_target')):
			shoes.AddSubstitution('pnum', "@pnum_source", '@pnum_target')

		# tnum
		# one > one.tf
		for glyph in shoes.GlyphsInGroup('.tf'):
			source = shoes.SourceGlyphFromTarget(glyph)
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@tnum_source', source)
				shoes.AddGlyphsToClass('@tnum_target', target)
		# one.osf > one.tosf
		for glyph in shoes.GlyphsInGroup('.tosf'):
			source = shoes.SourceGlyphFromTarget(glyph) + '.osf'
			target = glyph
			if shoes.HasGlyphs((source, target)):
				shoes.AddGlyphsToClass('@tnum_source', source)
				shoes.AddGlyphsToClass('@tnum_target', target)
		if shoes.HasClasses(('@tnum_source', '@tnum_target')):
			shoes.AddSubstitution('tnum', "@tnum_source", '@tnum_target')
	
	# case
	shoes.AddSimpleSubstitutionFeature('case', '.case')
	if shoes.HasClasses(('@lnum_source', '@lnum_target')):
		shoes.AddSubstitution('case', "@lnum_source", '@lnum_target')
	shoes.AddSimpleSubstitutionFeature('case', '.caps')
	
	
	# cpsp Capital Spacing
	if shoes.HasClasses('@uppercaseLetters'):
		shoes.AddSinglePositioning('cpsp', '@uppercaseLetters', (5, 0, 10, 0))

	if False:	
		# c2sc
		for g in shoes.GlyphsInGroup('.sc'):
			# remove .sc
			lowercase = shoes.SourceGlyphFromTarget(g)
			if f.glyphs():
				lowercaseglyph = f.glyphs[lowercase]
	#			if lowercaseglyph.unicode:
				if Unicode(lowercaseglyph):
	#				lowercaseUC = FP.Unicode.Unicode(FP.Dec2HexUnicode(lowercaseglyph.unicode))
					lowercaseUC = FP.Unicode.Unicode(Unicode(lowercaseglyph))
					# lowercase has uppercase mapping
					if lowercaseUC.othercase_hex_unicode:
						uppercaseUC = FP.Unicode.Unicode(lowercaseUC.othercase_hex_unicode)
						uppercaseglyph = f.glyphs[f.FindGlyph(Uni(uppercaseUC.hex_unicode))]
						# source glyph not yet present (avoid duplicates with longs and idotaccent)
						if not shoes.ClassHasGlyphs('@c2sc_source', uppercaseglyph.name):
							shoes.AddGlyphsToClass('@c2sc_source', uppercaseglyph.name)
							shoes.AddGlyphsToClass('@c2sc_target', g)
		if shoes.HasClasses(('@c2sc_source', '@c2sc_target')):
			shoes.AddSubstitution('c2sc', "@c2sc_source", '@c2sc_target')
	
		
	
	# Duplicate Features
	for source, target in duplicateFeatures:
		features.remove(target)
		features.insert(features.index(source) + 1, target)
		shoes.DuplicateFeature(source, target)

		if OTfeatures.has_key(source):
			shoes.SetStylisticSetName(target, OTfeatures[source])

	
	return shoes
	
