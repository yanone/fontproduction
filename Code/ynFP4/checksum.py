#!/usr/bin/python
# -*- coding: utf-8 -*-

import ynlib.fonts.fonttoolsstuff

# Settings
aesKey = 'K82KMH9ZsxuZh7ejc7xhGxAS'
identifier = u'Font integrity checksum, do not remove: '
nameID = 32137

def removeChecksums(identifier, f):
	# Remove checksum entry
	for name in f.TTFont.get('name').names:
		if name.string.startswith(str(identifier)):
			f.TTFont.get('name').names.remove(name)


def makeCheckSum(filepath, additionalValues = {}):
	import time, json, base64, shutil
	from ynlib.crypto.aes import encryptData, decryptData


	# Copy file
#	shutil.copyfile(filepath, filepath.replace('.otf', '.original.otf'))

	f = ynlib.fonts.fonttoolsstuff.Font(filepath, recalcTimestamp = False)
	removeChecksums(identifier, f)
	f.TTFont.save(filepath)
	f = ynlib.fonts.fonttoolsstuff.Font(filepath, recalcTimestamp = False)

	d = {
		'checksumVersion': '1.0',
		'creator': 'Yanone',
		'originalGenerator': 'n/a',
		'modifyingGenerator': 'n/a',
		'distributor': 'Yanone',
		'customer': 'post@yanone.de',
		'date': int(time.time()),
		'tableChecksums': f.tableChecksums(),
	}

	# Overwrite
	for key in additionalValues.keys():
		d[key] = additionalValues[key]

	string = identifier + base64.standard_b64encode(encryptData(aesKey, json.dumps(d)))
	f.TTFont.get('name').setName(string, nameID, 1, 0, 0)

	f.TTFont.save(filepath)

def checkChecksum(filepath):
	import time, json, base64
	from ynlib.crypto.aes import encryptData, decryptData

	errors = []

	try:
		f = ynlib.fonts.fonttoolsstuff.Font(filepath, recalcTimestamp = False)
	except:
		return False, 'File is not a font.'


	# Has checksum name entry
	if not f.TTFont.get('name').getName(nameID, 1, 0, 0):
		return False, 'Checksum is missing from file.'

	# Decode
	encoded = unicode(f.TTFont.get('name').getName(nameID, 1, 0, 0)).split(identifier)[-1]
	try:
		decoded = base64.standard_b64decode(encoded)
		d = json.loads(decryptData(aesKey, decoded))
	except:
		return False, 'Decryption of checksum failed.'

	# Format
	if not d.has_key('checksumVersion'):
		errors.append('Checksum format unknown.')

	# Creator
	if not d.has_key('creator') or d['creator'] != 'Yanone':
		errors.append('This font is not from Yanone.')

	# Remove + re-open
	removeChecksums(identifier, f)
	f.TTFont.save(filepath)
	f = ynlib.fonts.fonttoolsstuff.Font(filepath, recalcTimestamp = False)

	# Table checksums
	tableChecksums = f.tableChecksums()
	if not set(tableChecksums.keys()) == set(d['tableChecksums'].keys()):
		errors.append('Mismatch in stored table checksums.')
	for tableName in d['tableChecksums'].keys():
		if tableChecksums[tableName] != d['tableChecksums'][tableName]:
			errors.append('Table checksum mismatch for %s table.' % tableName)

	if errors:
		return False, '\n'.join(errors)
	else:
		return True, 'Font is authentic.'

#makeCheckSums()
#print checkChecksums()
