#!/usr/bin/python
# -*- coding: utf-8 -*-

import ynFP4, copy
from ynlib.files import WriteToFile
from ynlib.fonts.fonttoolsstuff import Font

def prepareForTrueTypeHintingTest(font):



	for i, glyph in enumerate(font.copy().glyphs):
		if not glyph.unicode:
			u = hex(int('F0000', 16) + i).split('0x')[1]
			font.glyphs[glyph.name].unicode = u
#			font.glyphs.storeProductionName = True
#			font.glyphs.productionName = 'uni%s' % u.upper()

	return font



waterFallStart = 8
waterFallEnd = 40


def addGlyphs(html, groupName, unicodes):
	html += '<div id="%s" class="waterfall">' % groupName
	unicodesHtml = ''
	for u in unicodes:
		unicodesHtml += '&#%s;' % int(u, 16)

	html += unicodesHtml

	html += '</div>'

	return html


def makeHintingTestPage(glyphsFont, fontpaths, htmlpath):

	fonts = []
	for fontpath in fontpaths:
		fonts.append(Font(fontpath))

	html = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Hinting Test ''' + str(fonts[0].postScriptName.split('-')[0]) + '''</title>
<link href="hinting.css" rel="stylesheet" type="text/css" />
<script type="text/javascript" src="js/jquery.js"></script>
<script type="text/javascript" src="js/hinting.js"></script>
<style>'''

	for font in fonts:
		html += '@font-face { font-family: "%s"; src: url("fonts/%s.ttf"); format(TrueType); }' % (font.postScriptName, font.postScriptName)

	html += '.waterfall { font-family: "%s"; }'	% fonts[0].postScriptName

	html += '''</style>
<script type="text/javascript">

fontSize = 10;

document.addEventListener('keydown', function(event) {
    console.log(event.keyCode);
    if(event.keyCode == 65) {
        fontSize += 1;
    }
    else if(event.keyCode == 83) {
        fontSize += 10;
    }
    else if(event.keyCode == 89) {
        fontSize -= 1;
    }
    else if(event.keyCode == 88) {
        fontSize -= 10;
    }
    else if(event.keyCode == 188) {
        fontSize = 10;
    }

    $('.waterfall').css('font-size', fontSize + 'px');
    $('.waterfall').css('line-height', fontSize * 1.3 + 'px');

    $('#fontSize').html(fontSize + 'px');
});

$( document ).ready(function() {
	show('base');
	$('.selector').click(function () {
		$('.selector').removeClass('selected');
		$(this).addClass('selected');
		
		$('.waterfall').css('font-size', fontSize + 'px');
	    $('.waterfall').css('line-height', fontSize * 1.3 + 'px');
	});
});

function show(name) {
	
	$('.waterfall').hide();
	$('#' + name + '.waterfall').show();

}

</script>
</head>

<body>
<div id="header" class="clear">
	<div id="fontSize" class="floatleft selector">
		10px
	</div>
	<div id="fonts" class="floatleft">
		<select onclick="$('.waterfall').css('font-family', $(this).val());">'''
	
	for font in fonts:
		html += '<option value="%s">%s</option>' % (font.postScriptName, font.postScriptName)
	html += '''
		</select>
	</div>
	<div class="floatleft selector">
		<a href="JavaScript:show('base');">Base glyphs</a>
	</div>
	<div class="floatleft selector">
		<a href="JavaScript:show('components');">Component glyphs</a>
	</div>
	<div class="floatleft selector">
		<a href="JavaScript:show('numbers');">Numbers</a>
	</div>
	<div class="floatleft selector">
		<a href="JavaScript:show('rest');">Rest</a>
	</div>
</div>

'''


	# Base glyphs
	usedUnicodes = []
	unicodes = []
	for glyph in glyphsFont.glyphs:
		if glyph.layers[0].paths and not glyph.layers[0].components and glyph.unicode and glyph.category and glyph.category.startswith('L'):
			unicodes.append(glyph.unicode)
			usedUnicodes.append(glyph.unicode)
	html = addGlyphs(html, 'base', unicodes)

	# Base glyphs
	unicodes = []
	for glyph in glyphsFont.glyphs:
		if glyph.layers[0].components and glyph.unicode and glyph.category and glyph.category.startswith('L'):
			unicodes.append(glyph.unicode)
			usedUnicodes.append(glyph.unicode)
	html = addGlyphs(html, 'components', unicodes)

	# Numbers glyphs
	unicodes = []
	for glyph in glyphsFont.glyphs:
		if glyph.unicode and glyph.category and glyph.category == 'Number':
			unicodes.append(glyph.unicode)
			usedUnicodes.append(glyph.unicode)
	html = addGlyphs(html, 'numbers', unicodes)

	# Rest
	unicodes = []
	for glyph in glyphsFont.glyphs:
		if glyph.unicode and not glyph.unicode in usedUnicodes:
			unicodes.append(glyph.unicode)
			usedUnicodes.append(glyph.unicode)
	html = addGlyphs(html, 'rest', unicodes)

	html += '''

</body>
</html>
'''
	


	WriteToFile(htmlpath, html)