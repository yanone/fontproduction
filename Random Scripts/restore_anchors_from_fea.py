classes = {}

re_classname = r"(.+?) = \["
re_sub = r".*sub dvmI' (.+?) by (.+?);"

with open("/Users/yanone/Projekte/Google/Onboarding/khand/styles/Black/pres_mI.fea", "r") as f:
    lines = [l.strip() for l in f.readlines()]

classname = None

for line in lines:

    # classes
    m = re.match(re_classname, line)
    if m:
        classname = m.group(1)
        continue

    if line == "];":
        classname = None
        continue

    # subs
    m = re.match(re_sub, line)
    if m:
        classname, matrai_glyphname = m.group(1), m.group(2)

        # apply
        if classname in classes:
            for glyphname in classes[classname]:
                matrai = font.glyphs[matrai_glyphname]
                print(matrai)
                x = matrai.layers[0].anchors["abvm.i"].x - matrai.layers[0].width
                Glyphs.fonts[1].glyphs[glyphname].layers[1].anchors["abvm.i"] = GSAnchor(
                    "abvm.i", (x, matrai.layers[0].anchors["abvm.i"].y)
                )
        continue

    if classname:
        if classname not in classes:
            classes[classname] = []
        classes[classname].append(line)
