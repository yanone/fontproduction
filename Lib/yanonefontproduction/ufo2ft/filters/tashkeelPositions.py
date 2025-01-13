import logging
import copy

from ufo2ft.filters import BaseFilter
from fontTools.pens.boundsPen import ControlBoundsPen

logger = logging.getLogger(__name__)


def _find_anchor(glyph, name):
    for anchor in glyph.anchors:
        if anchor.name == name:
            return anchor


def get_bounds(glyph, glyphset):
    try:
        pen = ControlBoundsPen(glyphset)
        glyph.draw(pen)
        return pen.bounds
    except Exception:
        return None


def move_top(target, source, glyph=None):
    if target and source:
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


class TashkeelPositionsFilter(BaseFilter):

    _kwargs = {"a": 0}

    # def __call__(self, font, glyphSet=None):
    #     if super().__call__(font, glyphSet):
    #         modified = self.context.modified
    #         if modified:
    #             logger.info("Adjusted mark positions: %i" % len(modified))
    #         return modified

    def glyphset(self):
        if not hasattr(self, "_glyphset"):
            self._glyphset = self.context.glyphSet
        return self._glyphset

    def filter(self, glyph):

        bounds = get_bounds(glyph, self.glyphset())
        dont = (".el" in glyph.name or ".swsh" in glyph.name) and glyph.width > 2000

        modified = False

        # Adjust anchors positions

        # Delete top and bottom anchors if glyph is a ligature
        # these are left-overs from marks and are not supposed to exist
        if (
            "_" in glyph.name
            and not glyph.name.startswith("_")
            and len(glyph.components) > 1
        ):
            if _find_anchor(glyph, "top"):
                del glyph.anchors[glyph.anchors.index(_find_anchor(glyph, "top"))]
            if _find_anchor(glyph, "bottom"):
                del glyph.anchors[glyph.anchors.index(_find_anchor(glyph, "bottom"))]

        swsh = ".swsh" in glyph.name
        el = ".el" in glyph.name
        normal = not swsh and not el
        wide = glyph.width > 2000
        narrow = glyph.width < 2000

        # SUKOON
        if _find_anchor(glyph, "mark_top") and _find_anchor(glyph, "top.sukoon"):
            _find_anchor(glyph, "top.sukoon").y = max(
                _find_anchor(glyph, "top.sukoon").y,
                _find_anchor(glyph, "mark_top").y,
            )
            modified = True
        if _find_anchor(glyph, "top") and _find_anchor(glyph, "top.sukoon"):
            _find_anchor(glyph, "top.sukoon").y = max(
                _find_anchor(glyph, "top.sukoon").y,
                _find_anchor(glyph, "top").y,
            )
            modified = True

        # TOP
        if _find_anchor(glyph, "top") and _find_anchor(glyph, "mark_top"):
            _find_anchor(glyph, "top").x = _find_anchor(glyph, "mark_top").x

            apply_margin = bounds and _find_anchor(glyph, "mark_top").y > bounds[3]

            if wide and el:
                _find_anchor(glyph, "top").y = _find_anchor(glyph, "mark_top").y

            else:
                _find_anchor(glyph, "top").y = max(
                    _find_anchor(glyph, "top").y,
                    _find_anchor(glyph, "mark_top").y,
                )

            # mark_top is too far from top
            # make them equal
            if (
                abs(_find_anchor(glyph, "top").x - _find_anchor(glyph, "mark_top").x)
                > 100
            ):
                _find_anchor(glyph, "top").x = _find_anchor(glyph, "mark_top").x
                _find_anchor(glyph, "top").y = _find_anchor(glyph, "mark_top").y

            # Top margin
            if bounds:
                if (normal or (el and narrow)) and apply_margin:  # swsh or

                    top_margin = 50
                    if swsh:
                        top_margin = 150

                    _find_anchor(glyph, "top").y = max(
                        _find_anchor(glyph, "top").y,
                        bounds[3] + top_margin,
                    )

            else:
                _find_anchor(glyph, "top").y = _find_anchor(glyph, "mark_top").y

            # # Top margin just for SWSH
            # if bounds and ".swsh" in glyph.name and glyph.width > 2000:
            #     top_margin = 250
            #     _find_anchor(glyph, "top").y = max(
            #         _find_anchor(glyph, "top").y,
            #         bounds[3] + top_margin,
            #     )

            modified = True

        # BOTTOM
        if _find_anchor(glyph, "bottom") and _find_anchor(glyph, "mark_bottom"):
            _find_anchor(glyph, "bottom").x = _find_anchor(glyph, "mark_bottom").x

            if ".swsh" in glyph.name:
                _find_anchor(glyph, "bottom").y = _find_anchor(glyph, "mark_bottom").y
            elif not dont:
                _find_anchor(glyph, "bottom").y = min(
                    _find_anchor(glyph, "bottom").y,
                    _find_anchor(glyph, "mark_bottom").y,
                )
            else:
                _find_anchor(glyph, "bottom").y = _find_anchor(glyph, "mark_bottom").y
            modified = True

        # Adjust anchor.y where topthreedots acnhor exists.
        # TODO: make this work for top* instead of just topthreedots
        if (
            _find_anchor(glyph, "topthreedots")
            and len(glyph.components) >= 2
            and _find_anchor(
                self.context.font[glyph.components[1].baseGlyph], "_topthreedots"
            )
        ):
            _find_anchor(glyph, "top").x = _find_anchor(glyph, "topthreedots").x
            _find_anchor(glyph, "top").y += (
                _find_anchor(self.context.font[glyph.components[1].baseGlyph], "top").y
                - _find_anchor(
                    self.context.font[glyph.components[1].baseGlyph], "_top"
                ).y
                - 150
            )

        # Ligatures
        if glyph.components:
            for i in range(len(glyph.components)):

                if _find_anchor(glyph, f"top_{i+1}") and _find_anchor(
                    glyph, f"mark_top_{i+1}"
                ):
                    _find_anchor(glyph, f"top_{i+1}").x = _find_anchor(
                        glyph, f"mark_top_{i+1}"
                    ).x
                    _find_anchor(glyph, f"top_{i+1}").y = _find_anchor(
                        glyph, f"mark_top_{i+1}"
                    ).y
                    modified = True

                if _find_anchor(glyph, f"bottom_{i+1}") and _find_anchor(
                    glyph, f"mark_bottom_{i+1}"
                ):
                    _find_anchor(glyph, f"bottom_{i+1}").x = _find_anchor(
                        glyph, f"mark_bottom_{i+1}"
                    ).x
                    _find_anchor(glyph, f"bottom_{i+1}").y = _find_anchor(
                        glyph, f"mark_bottom_{i+1}"
                    ).y
                    modified = True

        return modified
