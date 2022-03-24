import logging

from ufo2ft.filters import BaseFilter

logger = logging.getLogger(__name__)


def _find_anchor(glyph, name):
    for anchor in glyph.anchors:
        if anchor.name == name:
            return anchor


def _anchors_contains_name(glyph, name):
    return [a.name for a in glyph.anchors if name in a.name]


class MarkPosFilter(BaseFilter):

    _kwargs = {"a": 0}

    def __call__(self, font, glyphSet=None):
        if super().__call__(font, glyphSet):
            modified = self.context.modified
            if modified:
                logger.info("Adjusted mark positions: %i" % len(modified))
            return modified

    def filter(self, glyph):

        modified = False

        # Remove _mark_top and _mark_bottom
        for anchor in glyph.anchors:
            if "_mark" in anchor.name:
                glyph.anchors.remove(anchor)
        # if _anchors_contains_name(glyph, "_mark"):
        #     glyph.anchors = list(
        #         set(glyph.anchors) - set()
        #     )

        # Adjust anchors positions
        if glyph.components:
            baseComponent = self.context.font[glyph.components[0].baseGlyph]

            for sourceGlyph in (glyph, baseComponent):
                for anchor in _anchors_contains_name(glyph, "top"):
                    if _find_anchor(glyph, "top") and _find_anchor(sourceGlyph, anchor):
                        _find_anchor(glyph, "top").x = min(
                            _find_anchor(glyph, "top").x, _find_anchor(sourceGlyph, anchor).x
                        )
                        _find_anchor(glyph, "top").y = max(
                            _find_anchor(glyph, "top").y, _find_anchor(sourceGlyph, anchor).y
                        )
                        modified = True

            for sourceGlyph in (glyph, baseComponent):
                for anchor in _anchors_contains_name(glyph, "bottom"):
                    if _find_anchor(glyph, "bottom") and _find_anchor(sourceGlyph, anchor):
                        _find_anchor(glyph, "bottom").x = min(
                            _find_anchor(glyph, "bottom").x, _find_anchor(sourceGlyph, anchor).x
                        )
                        _find_anchor(glyph, "bottom").y = min(
                            _find_anchor(glyph, "bottom").y, _find_anchor(sourceGlyph, anchor).y
                        )
                        modified = True

            # Ligatures
            for i in range(len(glyph.components)):
                baseComponent = self.context.font[glyph.components[i].baseGlyph]

                for sourceGlyph in (glyph, baseComponent):
                    # for anchor in _anchors_contains_name(glyph, "top"):
                    if _find_anchor(glyph, f"top_{i+1}") and _find_anchor(baseComponent, "mark_top"):
                        _find_anchor(glyph, f"top_{i+1}").x = min(
                            _find_anchor(glyph, f"top_{i+1}").x, _find_anchor(baseComponent, "mark_top").x
                        )
                        _find_anchor(glyph, f"top_{i+1}").y = max(
                            _find_anchor(glyph, f"top_{i+1}").y, _find_anchor(baseComponent, "mark_top").y
                        )
                        modified = True

                for sourceGlyph in (glyph, baseComponent):
                    # for anchor in _anchors_contains_name(glyph, "bottom"):
                    if _find_anchor(glyph, f"bottom_{i+1}") and _find_anchor(baseComponent, "mark_bottom"):
                        _find_anchor(glyph, f"bottom_{i+1}").x = min(
                            _find_anchor(glyph, f"bottom_{i+1}").x, _find_anchor(baseComponent, "mark_bottom").x
                        )
                        _find_anchor(glyph, f"bottom_{i+1}").y = min(
                            _find_anchor(glyph, f"bottom_{i+1}").y, _find_anchor(baseComponent, "mark_bottom").y
                        )
                        modified = True

        # Glyphs with outlines
        for anchor in _anchors_contains_name(glyph, "top"):
            if _find_anchor(glyph, "top") and _find_anchor(glyph, anchor):
                _find_anchor(glyph, "top").x = min(_find_anchor(glyph, "top").x, _find_anchor(glyph, anchor).x)
                _find_anchor(glyph, "top").y = max(_find_anchor(glyph, "top").y, _find_anchor(glyph, anchor).y)
                modified = True

        for anchor in _anchors_contains_name(glyph, "bottom"):
            if _find_anchor(glyph, "bottom") and _find_anchor(glyph, anchor):
                _find_anchor(glyph, "bottom").x = min(_find_anchor(glyph, "bottom").x, _find_anchor(glyph, anchor).x)
                _find_anchor(glyph, "bottom").y = min(_find_anchor(glyph, "bottom").y, _find_anchor(glyph, anchor).y)
                modified = True

        # Ligatures
        # if _find_anchor(glyph, f"top_{i+1}") and _find_anchor(glyph, "mark_top"):
        #     _find_anchor(glyph, f"top_{i+1}").x = min(
        #         _find_anchor(glyph, f"top_{i+1}").x, _find_anchor(glyph, "mark_top").x
        #     )
        #     _find_anchor(glyph, f"top_{i+1}").y = max(
        #         _find_anchor(glyph, f"top_{i+1}").y, _find_anchor(glyph, "mark_top").y
        #     )
        #     modified = True

        # if _find_anchor(glyph, f"bottom_{i+1}") and _find_anchor(glyph, "mark_bottom"):
        #     _find_anchor(glyph, f"bottom_{i+1}").x = min(
        #         _find_anchor(glyph, f"bottom_{i+1}").x, _find_anchor(glyph, "mark_bottom").x
        #     )
        #     _find_anchor(glyph, f"bottom_{i+1}").y = min(
        #         _find_anchor(glyph, f"bottom_{i+1}").y, _find_anchor(glyph, "mark_bottom").y
        #     )
        #     modified = True

        return modified
