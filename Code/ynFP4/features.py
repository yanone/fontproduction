#!/usr/bin/python
# -*- coding: utf-8 -*-

import unicodedata, os, string
import dancingshoes
reload(dancingshoes)
import dancingshoes.helpers
reload(dancingshoes.helpers)

import ynFP4
reload(ynFP4)
from dancingshoes import DancingShoes
from ynlib.fonts.opentypenames import OTfeatures

from dancingshoes.helpers import GlyphNamesFromGlyphsFont, SubstitutionsFromCSV

def makeFeatures(font):

	import copy

	print 'Dancing with my new shoes...'

	shoes = MakeDancingShoes(font, GlyphNamesFromGlyphsFont(font), stylisticsetnames = ynFP4.stylisticSetNames)

	# Apply code
	from dancingshoes.helpers import AssignFeatureCodeToGlyphsFont
	AssignFeatureCodeToGlyphsFont(font, shoes)

	# Glyphs' features
	# onum = font.features['onum']
	font.updateFeatures()
	features = copy.copy(font.features)
	features.sort(key=lambda x: ynFP4.featureOrder.index(x.name))
	font.features = features
	# if not onum:
	# 	del(font.features['onum'])

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
		['subs', 'sinf'],
		['hist', 'ss18'],
		['zero', 'ss19'],
		['salt', 'ss20'],
	]



	if not features:		
		features = ynFP4.featureOrder

#	print features
	
	
	# Initialize DancingShoes object, hand over glyph names and default features
	shoes = DancingShoes(glyphnames, features)

	# Set stylistic set names
	if stylisticsetnames:
		for ssname in stylisticsetnames:
			shoes.SetStylisticSetName(ssname, stylisticsetnames[ssname])


	# UppercaseLetters
	for g in f.glyphs:
		if g.unicode and unicodedata.category(g.string) == 'Lu':
			shoes.AddGlyphsToClass('@uppercaseLetters', g.name)

	# LowercaseLetters
	for g in f.glyphs:
		if g.unicode and unicodedata.category(g.string) == 'Ll':
			shoes.AddGlyphsToClass('@lowercaseLetters', g.name)

	# Numbers
	shoes.AddGlyphsToClass('@numbers', ("zero","one","two","three","four","five","six","seven","eight","nine"))


	# Various classes from Glyphs
	for g in f.glyphs:
		if g.userData:
			if g.userData['OTclass']:
				for OTclass in g.userData['OTclass']:
					shoes.AddGlyphsToClass('@' + OTclass, g.name)


	
	# Add direct substitutions
	directsubstitutions = (
		('smcp', '.sc'),
		('salt', '.salt'),
		('sups', '.sups'),
		('subs', '.subs'),
		('swsh', '.swsh'),
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



	#SUBS/SINF
	for name in shoes.Glyphs():
		if 'inferior' in name:
			source = name.replace('inferior', '')
			target = name
			shoes.AddSubstitution('subs', source, target)

	#LOCL
	for name in shoes.Glyphs():
		if 'locl_' in name.split('.')[-1]:
			featureName, script, language = name.split('.')[-1].split('_')
			shoes.AddSubstitution('locl', name.split('.')[0], name, script, language)

		elif 'locl' in name.split('.')[-1]:
			script = 'latn'
			language = name.split('.')[-1][4:]
			shoes.AddSubstitution('locl', name.split('.')[0], name, script, language)



	#DLIG
	for name in shoes.Glyphs():
		if '.dlig' in name:
			names = name[:-5].split('_')
			if shoes.HasGlyphs(names):
				shoes.AddSubstitution('dlig', ' '.join(names), name)
				
	#LIGA
	for name in shoes.Glyphs():
		if '.liga' in name:
			names = name[:-5].split('_')
			if shoes.HasGlyphs(names):
				shoes.AddSubstitution('liga', ' '.join(names), name)

	# Fraction feature
	if shoes.HasGroups(['.numr', '.dnom']) and shoes.HasGlyphs(['fraction']):
		shoes.AddSimpleSubstitutionFeature('numr', '.numr')
		shoes.AddSimpleSubstitutionFeature('dnom', '.dnom')
		
		shoes.AddGlyphsToClass('fractionslashes', ['slash', 'fraction'])
		shoes.AddSubstitution('frac', '@numr_source', '@numr_target')
		shoes.AddSubstitution('frac', 'slash', 'fraction')
		shoes.AddSubstitution('frac', "[@fractionslashes @dnom_target] @numr_target'", '@dnom_target')
	
	# ß im Versalsatz
	if shoes.HasGlyphs(['Germandbls', 'germandbls']):
		shoes.AddSubstitution('calt', "@uppercaseLetters germandbls'", 'Germandbls')


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
		elif name.endswith('.sups.caps'):
			if unicodedata.category(unichr(int(f.glyphs[name.split('.')[0]].unicode, 16)).upper()) == 'Lu':
				
				lowercaseGlyphName = name.split('.')[0]
				uppercaseGlyphName = f.glyphs[f.glyphs[lowercaseGlyphName].string.upper()].name
				shoes.AddGlyphsToClass('@ordn_source', uppercaseGlyphName)
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

	# c2sc
	for name in shoes.Glyphs():
		if name.endswith('.sc') and not 'longs' in name:
			lowercaseGlyphName = name.split('.')[0]

			specialCase = ['idotaccent']

			if f.glyphs[lowercaseGlyphName] and f.glyphs[lowercaseGlyphName].unicode and unicodedata.category(unichr(int(f.glyphs[lowercaseGlyphName].unicode, 16))) == 'Ll' or lowercaseGlyphName in specialCase:

				# special case
				if lowercaseGlyphName == 'germandbls':
					uppercaseGlyphName = 'Germandbls'

				elif lowercaseGlyphName == 'idotaccent':
					uppercaseGlyphName = 'Idotaccent'

				else:
					uppercaseGlyphName = f.glyphs[f.glyphs[lowercaseGlyphName].string.upper()].name


				if lowercaseGlyphName.startswith('i'):
					print name, lowercaseGlyphName, uppercaseGlyphName

				# # special case
				# if lowercaseGlyphName == 'idotaccent':
				# 	uppercaseGlyphName = 'Idotaccent'

				if shoes.HasGlyphs([uppercaseGlyphName, name]) and not uppercaseGlyphName in shoes.GlyphsInClass('@c2sc_source'):
					shoes.AddGlyphsToClass('@c2sc_source', uppercaseGlyphName)
					shoes.AddGlyphsToClass('@c2sc_target', name)

	if shoes.HasClasses(('@c2sc_source', '@c2sc_target')):
		shoes.AddSubstitution('c2sc', "@c2sc_source", '@c2sc_target')

	# SMCP
	if shoes.HasClasses(('@lnum_source', '@lnum_target')):
		shoes.AddSubstitution('smcp', "@lnum_source", '@lnum_target')
		shoes.AddSubstitution('c2sc', "@lnum_source", '@lnum_target')

	# ARABIC
	
#	if shoes.HasGroups('.arab'):
#		shoes.AddEndingToBothClasses('arab', '.arab')
#		shoes.AddSubstitution('locl', "@arab_source", '@arab_target', 'arab', '', 'RightToLeft')
		
	
	# SCRIPT MAGIC

	automaticCaltConnection = []
	doubleCaltConnections = []
	doubleCaltGlyphs = []

	for glyph in shoes.Glyphs():
		if '.conn-' in glyph:
			

			baseGlyphName = None
			double = None
			parts = glyph.split('.')

			# Gather how many same-named parts there are
			names = {}
			for part in parts:
				if 'conn-' in part:
					name = part.split('-')[1]
					if not name in names:
						names[name] = 1
					else:
						names[name] += 1

			for name in names:
				if names[name] > 1:
					double = name

			# We have double
			if double:
				print 'glyph %s has two name parts of same group: %s' % (glyph, double)


			# Go through name parts
			for i, part in enumerate(parts):

				if 'conn-' in part:

					#bareGlyphName, ending = parts[-1].split('conn-')
					bareGlyphName = '.'.join(parts[:i])
					if not baseGlyphName:
						baseGlyphName = bareGlyphName
					glyph = '.'.join(parts[:i+1])

					ending = part.split('conn-')[-1]
					ending = '.conn-' + ending
					connectionName, position = ending.split('-')[1:]

					if '_' in connectionName:
						lookupName = 'glyphNameBasedConnections_%s' % connectionName.split('_')[-1]
					else:
						lookupName = 'glyphNameBasedConnections'

					listItem = (connectionName, 'glyphNameBasedConnections')

					if not listItem in automaticCaltConnection:
						automaticCaltConnection.append(listItem)



					if shoes.HasGlyphs([bareGlyphName, glyph]):
						shoes.AddGlyphsToClass('@conn_%s_%s_source' % (connectionName, position), bareGlyphName)
						shoes.AddGlyphsToClass('@conn_%s_%s_target' % (connectionName, position), glyph)

					if double:

						className = '@conn_%s_trigger' % (connectionName)
						for g in (glyph, baseGlyphName, bareGlyphName):
							if not shoes.HasClasses(className) or not g in shoes.GlyphsInClass(className):
								shoes.AddGlyphsToClass(className, g)


						listItem = ['calt', "@conn_%s_trigger @conn_%s_2_source'" % (connectionName, connectionName), '@conn_%s_2_target' % connectionName, 'arab', '', 'RightToLeft,IgnoreMarks', connectionName, '%s_%s_2' % (lookupName, connectionName)]
						if not listItem in doubleCaltConnections:
							doubleCaltConnections.append(listItem)


	for i, values in enumerate(sorted(automaticCaltConnection)):
		connectionName, lookupName = values
		shoes.AddSubstitution('calt', "@conn_%s_1_source' @conn_%s_2_source" % (connectionName, connectionName), '@conn_%s_1_target' % connectionName, 'arab', '', 'RightToLeft,IgnoreMarks', connectionName, '%s_%s' % (lookupName, connectionName))
		shoes.AddSubstitution('calt', "@conn_%s_1_target @conn_%s_2_source'" % (connectionName, connectionName), '@conn_%s_2_target' % connectionName, 'arab', '', 'RightToLeft,IgnoreMarks', connectionName, '%s_%s' % (lookupName, connectionName))

		for g in shoes.GlyphsInClass('@conn_%s_1_target' % connectionName):
			shoes.AddGlyphsToClass('@conn_%s_trigger' % (connectionName), g)



	for line in doubleCaltConnections:
		shoes.AddSubstitution(*line)

#		shoes.AddSubstitution('calt', "@conn_%s_2_target @conn_%s_2_source'" % (connectionName, connectionName), '@conn_%s_2_target' % connectionName, 'arab', '', 'RightToLeft,IgnoreMarks', connectionName, '%s_%s' % (lookupName, i))



	if shoes.HasGroups(['.lohi', '.hi']):

		if shoes.HasGroups(['.hilo']):
			for glyph in shoes.Glyphs():
				if '.hilo' in glyph:
					if shoes.HasGlyphs([glyph, glyph.replace('.lohi', '')]):
						shoes.AddGlyphsToClass('@arabmedihilo_source', glyph.replace('.hilo', ''))
						shoes.AddGlyphsToClass('@arabmedihilo_target', glyph)
			shoes.AddSubstitution('calt', "@arabmedilohi_source' @arabmedihilo_source", '@arabmedilohi_target', 'arab', '', 'RightToLeft,IgnoreMarks')
			shoes.AddSubstitution('calt', "@arabmedilohi_target @arabmedihilo_source'", '@arabmedihilo_target', 'arab', '', 'RightToLeft,IgnoreMarks')


		for glyph in shoes.Glyphs():
			if '.lohi' in glyph:
				if shoes.HasGlyphs([glyph, glyph.replace('.lohi', '')]):
					shoes.AddGlyphsToClass('@arabmedilohi_source', glyph.replace('.lohi', ''))
					shoes.AddGlyphsToClass('@arabmedilohi_target', glyph)
			if '.hi' in glyph:
				if shoes.HasGlyphs([glyph, glyph.replace('.hi', '')]):
					shoes.AddGlyphsToClass('@arabfinahi_source', glyph.replace('.hi', ''))
					shoes.AddGlyphsToClass('@arabfinahi_target', glyph)
		shoes.AddSubstitution('calt', "@arabmedilohi_source' @arabfinahi_source", '@arabmedilohi_target', 'arab', '', 'RightToLeft,IgnoreMarks')
		shoes.AddSubstitution('calt', "@arabmedilohi_target @arabfinahi_source'", '@arabfinahi_target', 'arab', '', 'RightToLeft,IgnoreMarks')


	# Additional swashes
	if shoes.HasGroups(['.swsh']):

		for glyph in shoes.Glyphs():
			if '.swsh' in glyph:
				if shoes.HasGlyphs([glyph.replace('.swsh', '.hitooth')]):
					shoes.AddSubstitution('swsh', glyph.replace('.swsh', '.hitooth'), glyph, 'arab', '', 'RightToLeft,IgnoreMarks')
				if shoes.HasGlyphs([glyph.replace('.swsh', '.dotColl')]):
					shoes.AddSubstitution('swsh', glyph.replace('.swsh', '.dotColl'), glyph, 'arab', '', 'RightToLeft,IgnoreMarks')

	

		# if shoes.HasGroups(['.lohi', '.hihi']):
		# 	for glyph in shoes.Glyphs():
		# 		if '.init.hihi' in glyph:
		# 			if shoes.HasGlyphs([glyph, glyph.replace('.hihi', '.lohi')]):
		# 				shoes.AddGlyphsToClass('@arabmedihihi_source', glyph.replace('.hihi', '.lohi'))
		# 				shoes.AddGlyphsToClass('@arabmedihihi_target', glyph)
		# 			if shoes.HasGlyphs([glyph, glyph.replace('.hihi', '')]):
		# 				shoes.AddGlyphsToClass('@arabmedihihi_source', glyph.replace('.hihi', ''))
		# 				shoes.AddGlyphsToClass('@arabmedihihi_target', glyph)
		# 	for glyph in shoes.Glyphs():
		# 		if '.fina.hihi' in glyph:
		# 			if shoes.HasGlyphs([glyph, glyph.replace('.hihi', '.hi')]):
		# 				shoes.AddGlyphsToClass('@arabfinahihi_source', glyph.replace('.hihi', '.hi'))
		# 				shoes.AddGlyphsToClass('@arabfinahihi_target', glyph)
		# 			if shoes.HasGlyphs([glyph, glyph.replace('.fina.hihi', '.fina')]):
		# 				shoes.AddGlyphsToClass('@arabfinahihi_source', glyph.replace('.fina.hihi', '.fina'))
		# 				shoes.AddGlyphsToClass('@arabfinahihi_target', glyph)
		# 	shoes.AddSubstitution('calt', "@arabmedihihi_source' @arabfinahihi_source", '@arabmedihihi_target', 'arab', '', 'RightToLeft,IgnoreMarks', '', 'behyeh')
		# 	shoes.AddSubstitution('calt', "@arabmedihihi_target @arabfinahihi_source'", '@arabfinahihi_target', 'arab', '', 'RightToLeft,IgnoreMarks', '', 'behyeh')



	# dot collisions
	if shoes.HasClasses(['@dotCollisionTop']):
		for glyph in shoes.GlyphsInClass('@dotCollisionTop'):
			if shoes.HasGlyphs([glyph, glyph.replace('.dotColl', '')]):
				shoes.AddGlyphsToClass('@dotCollTop_source', glyph.replace('.dotColl', ''))
				shoes.AddGlyphsToClass('@dotCollTop_target', glyph)
		shoes.AddSubstitution('calt', "@dotCollTop_source' @dotCollTop_source", '@dotCollTop_target', 'arab', '', 'RightToLeft,IgnoreMarks')
	if shoes.HasClasses(['@dotCollisionBottom']):
		for glyph in shoes.GlyphsInClass('@dotCollisionBottom'):
			if shoes.HasGlyphs([glyph, glyph.replace('.dotColl', '')]):
				shoes.AddGlyphsToClass('@dotCollBottom_source', glyph.replace('.dotColl', ''))
				shoes.AddGlyphsToClass('@dotCollBottom_target', glyph)
		shoes.AddSubstitution('calt', "@dotCollBottom_source' @dotCollBottom_source", '@dotCollBottom_target', 'arab', '', 'RightToLeft,IgnoreMarks')

		if shoes.HasClasses(['@dotCollBottomTrigger']):
			shoes.AddSubstitution('calt', "@dotCollBottom_source' @dotCollBottomTrigger", '@dotCollBottom_target', 'arab', '', 'RightToLeft,IgnoreMarks')

		if shoes.HasClasses(['@dotCollTopTrigger']):
			shoes.AddSubstitution('calt', "@dotCollTop_source' @dotCollTopTrigger", '@dotCollTop_target', 'arab', '', 'RightToLeft,IgnoreMarks')

	# HIGH TEETH
	if shoes.HasGroups(['.hitooth']) and shoes.HasClasses(('@seen_init', '@beh_fina')):

		for glyph in shoes.Glyphs():
			if '.hitooth' in glyph:
				if shoes.HasGlyphs([glyph, glyph.replace('.hitooth', '')]):
					shoes.AddGlyphsToClass('@hitooth_source', glyph.replace('.hitooth', ''))
					shoes.AddGlyphsToClass('@hitooth_target', glyph)
		shoes.AddSubstitution('calt', "@seen_init @hitooth_source'", '@hitooth_target', 'arab', '', 'RightToLeft,IgnoreMarks', '', 'dotColl')


	# YEH BARREE
	if shoes.HasClasses(['@yehBarreeShortTrigger', '@yehBarreeAlt']):
		for glyph in shoes.GlyphsInClass('@yehBarreeAlt'):
			if shoes.HasGlyphs([glyph, glyph.replace('.alt', '')]):
				shoes.AddGlyphsToClass('@yehBarreeAlt_source', glyph.replace('.alt', ''))
				shoes.AddGlyphsToClass('@yehBarreeAlt_target', glyph)
		shoes.AddSubstitution('calt', "@yehBarreeShortTrigger @yehBarreeAlt_source'", '@yehBarreeAlt_target', 'arab', '', 'RightToLeft,IgnoreMarks')

	# TOP MARKS and SHORT GLYPHS
	if shoes.HasGroups('.short') and shoes.HasClasses('@topMarks'):
		for glyph in shoes.Glyphs():
			if '.short' in glyph:
				if shoes.HasGlyphs([glyph, glyph.replace('.short', '')]):
					shoes.AddGlyphsToClass('@shortGlyphs_source', glyph.replace('.short', ''))
					shoes.AddGlyphsToClass('@shortGlyphs_target', glyph)
		shoes.AddSubstitution('calt', "@shortGlyphs_source' @topMarks", '@shortGlyphs_target', 'arab', '', 'RightToLeft')



	# Duplicate Features
	for source, target in duplicateFeatures:
		features.remove(target)
		features.insert(features.index(source) + 1, target)
		shoes.DuplicateFeature(source, target)

		if target.startswith('ss') and OTfeatures.has_key(source):
			shoes.SetStylisticSetName(target, OTfeatures[source])

	
	# Custom font code
	if f.note:
		exec(f.note)


	return shoes
	
