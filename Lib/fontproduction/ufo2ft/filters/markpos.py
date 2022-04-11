import logging
import copy

from ufo2ft.filters import BaseFilter
from fontTools.pens.boundsPen import ControlBoundsPen

logger = logging.getLogger(__name__)


def _find_anchor(glyph, name):
    for anchor in glyph.anchors:
        if anchor.name == name:
            return anchor


def _anchors_contains_name(glyph, name):
    return [a.name for a in glyph.anchors if name in a.name]


def _anchors_startswith_name(glyph, name):
    return [a.name for a in glyph.anchors if a.name.startswith(name)]


def get_controlPointBounds(glyph):
    try:
        pen = ControlBoundsPen(None)
        glyph.draw(pen)
        return pen.bounds
    except Exception:
        return None


def move_top(target, source, glyph=None):
    if target and source:
        # if glyph.name == "heh-ar.init.swsh":
        #     print(target.x, source.x)
        # if target.x - source.x < 400:
        target.x = min(target.x, source.x)
        target.y = max(target.y, source.y)
        return True
    return False


def move_bottom(target, source):
    if target and source:
        target.x = min(target.x, source.x)
        target.y = min(target.y, source.y)
        return True
    return False


class MarkPosFilter(BaseFilter):

    _kwargs = {"a": 0}

    def __call__(self, font, glyphSet=None):
        if super().__call__(font, glyphSet):
            modified = self.context.modified
            if modified:
                logger.info("Adjusted mark positions: %i" % len(modified))
            return modified

    def filter(self, glyph):

        # logging.error(glyph)

        modified = False

        # original_top = copy.copy(_find_anchor(glyph, "top"))
        # original_mark_top = copy.copy(_find_anchor(glyph, "mark_top"))

        # if glyph.name == "alefHamzaabove-ar":
        #     print(glyph.anchors)

        # Remove _mark_top and _mark_bottom
        for anchor in glyph.anchors:
            if "_mark" in anchor.name:
                glyph.anchors.remove(anchor)

        # Adjust anchors positions

        # for target_anchor_name in _anchors_startswith_name(glyph, "top"):
        if _find_anchor(glyph, "top") and _find_anchor(glyph, "mark_top"):
            # _find_anchor(glyph, "top").x = _find_anchor(glyph, "mark_top").x
            _find_anchor(glyph, "top").y = max(_find_anchor(glyph, "top").y, _find_anchor(glyph, "mark_top").y)
            if abs(_find_anchor(glyph, "top").x - _find_anchor(glyph, "mark_top").x) > 100:
                _find_anchor(glyph, "top").x = _find_anchor(glyph, "mark_top").x
                _find_anchor(glyph, "top").y = _find_anchor(glyph, "mark_top").y
            modified = True

        if _find_anchor(glyph, "bottom") and _find_anchor(glyph, "mark_bottom"):
            # _find_anchor(glyph, "bottom").x = _find_anchor(glyph, "mark_bottom").x
            _find_anchor(glyph, "bottom").y = min(
                _find_anchor(glyph, "bottom").y, _find_anchor(glyph, "mark_bottom").y
            )
            modified = True

        # Adjust anchor.y where topthreedots acnhor exists.
        # TODO: make this work for top* instead of just topthreedots
        if (
            _find_anchor(glyph, "topthreedots")
            and len(glyph.components) >= 2
            and _find_anchor(self.context.font[glyph.components[1].baseGlyph], "_topthreedots")
        ):
            # print(glyph, _find_anchor(glyph, "top").y)
            _find_anchor(glyph, "top").x = _find_anchor(glyph, "topthreedots").x
            _find_anchor(glyph, "top").y += (
                _find_anchor(self.context.font[glyph.components[1].baseGlyph], "top").y
                - _find_anchor(self.context.font[glyph.components[1].baseGlyph], "_top").y
                - 150
            )
            # for anchor in _anchors_contains_name(glyph, "top"):
            #     modified_this = move_top(_find_anchor(glyph, "top"), _find_anchor(glyph, anchor), glyph)
            #     if modified_this:
            #         modified = True

            # for anchor in _anchors_contains_name(glyph, "bottom"):
            #     modified_this = move_bottom(_find_anchor(glyph, "bottom"), _find_anchor(glyph, anchor))
            #     if modified_this:
            #         modified = True

        # Ligatures
        if glyph.components:
            for i in range(len(glyph.components)):

                if _find_anchor(glyph, f"top_{i+1}") and _find_anchor(glyph, f"mark_top_{i+1}"):
                    _find_anchor(glyph, f"top_{i+1}").x = _find_anchor(glyph, f"mark_top_{i+1}").x
                    _find_anchor(glyph, f"top_{i+1}").y = _find_anchor(glyph, f"mark_top_{i+1}").y
                    modified = True

                if _find_anchor(glyph, f"bottom_{i+1}") and _find_anchor(glyph, f"mark_bottom_{i+1}"):
                    _find_anchor(glyph, f"bottom_{i+1}").x = _find_anchor(glyph, f"mark_bottom_{i+1}").x
                    _find_anchor(glyph, f"bottom_{i+1}").y = _find_anchor(glyph, f"mark_bottom_{i+1}").y
                    modified = True

        #         modified_this = move_top(
        #             _find_anchor(glyph, f"top_{i+1}"), _find_anchor(glyph, f"mark_top_{i+1}"), glyph
        #         )
        #         if modified_this:
        #             modified = True

        #         modified_this = move_bottom(
        #             _find_anchor(glyph, f"bottom_{i+1}"), _find_anchor(glyph, f"mark_bottom_{i+1}")
        #         )
        #         if modified_this:
        #             modified = True

        # # Glyphs with outlines
        # for anchor in _anchors_contains_name(glyph, "top"):
        #     modified_this = move_top(_find_anchor(glyph, "top"), _find_anchor(glyph, anchor), glyph)
        #     if modified_this:
        #         modified = True

        # for anchor in _anchors_contains_name(glyph, "bottom"):
        #     modified_this = move_bottom(_find_anchor(glyph, "bottom"), _find_anchor(glyph, anchor))
        #     if modified_this:
        #         modified = True

        # # If new top anchor is too far off from the original,
        # # adjust its y position to the original mark_top.y
        # if original_top and original_mark_top and _find_anchor(glyph, "top"):
        #     if original_top.x - _find_anchor(glyph, "top").x > 400:
        #         _find_anchor(glyph, "top").y = original_mark_top.y
        #         modified = True

        # # Adjust upwards of bbox is high
        # if _find_anchor(glyph, "top"):
        #     bounds = get_controlPointBounds(glyph)
        #     if bounds:
        #         yMax = bounds[3]
        #         _find_anchor(glyph, "top").y = max(_find_anchor(glyph, "top").y, yMax - 100)
        #         modified = True

        #         print("adjusted", glyph.name)

        return modified
