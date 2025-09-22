import logging
import copy

from ufo2ft.filters import BaseFilter
from fontTools.pens.boundsPen import ControlBoundsPen

logger = logging.getLogger(__name__)


def anchor(glyph, name):
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

    def glyphset(self):
        if not hasattr(self, "_glyphset"):
            self._glyphset = self.context.glyphSet
        return self._glyphset

    def get_glyph(self, name):
        return self.context.font[name]

    def get_base_glyph(self, glyph):
        if glyph.components:
            for component in glyph.components:
                base_glyph = self.get_base_glyph(self.get_glyph(component.baseGlyph))
                if anchor(base_glyph, "top"):
                    return base_glyph
        return glyph

    def filter(self, glyph):

        VERBOSE = False

        bounds = get_bounds(glyph, self.glyphset())

        modified = False

        # Add _top.sukoon anchor for mark ligatures
        if glyph.components:
            all_component_have_sukoon_anchor = []
            for component in glyph.components:
                if component.baseGlyph in self.context.font:
                    base = self.context.font[component.baseGlyph]
                    if anchor(base, "_top.sukoon"):
                        all_component_have_sukoon_anchor.append(True)
            if (
                all_component_have_sukoon_anchor
                and all(all_component_have_sukoon_anchor)
                and len(all_component_have_sukoon_anchor) == len(glyph.components)
                and anchor(glyph, "_top")
                and not anchor(glyph, "_top.sukoon")
            ):
                new_anchor = copy.copy(anchor(glyph, "_top"))
                new_anchor.name = "_top.sukoon"
                glyph.anchors.append(new_anchor)
                modified = True

        # Adjust anchors positions

        # Delete top and bottom anchors if glyph is a ligature
        # these are left-overs from marks and are not supposed to exist
        if (
            "_" in glyph.name
            and not glyph.name.startswith("_")
            and len(glyph.components) > 1
        ):
            if anchor(glyph, "top"):
                del glyph.anchors[glyph.anchors.index(anchor(glyph, "top"))]
            if anchor(glyph, "bottom"):
                del glyph.anchors[glyph.anchors.index(anchor(glyph, "bottom"))]

        swsh = ".swsh" in glyph.name
        el = ".el" in glyph.name
        normal = not swsh and not el
        wide = glyph.width > 2000
        narrow = glyph.width < 2000

        # SUKOON
        if not (swsh and wide):
            if anchor(glyph, "mark_top") and anchor(glyph, "top.sukoon"):
                anchor(glyph, "top.sukoon").y = max(
                    anchor(glyph, "top.sukoon").y,
                    anchor(glyph, "mark_top").y,
                )
                modified = True
            if anchor(glyph, "top") and anchor(glyph, "top.sukoon"):
                anchor(glyph, "top.sukoon").y = max(
                    anchor(glyph, "top.sukoon").y,
                    anchor(glyph, "top").y,
                )
                modified = True

        # TOP
        if anchor(glyph, "top") and anchor(glyph, "mark_top"):

            top_and_mark_top_wide_apart_horizontally = (
                anchor(glyph, "top").x - anchor(glyph, "mark_top").x > 500
            )
            top_above_bbox = anchor(glyph, "top").y > bounds[3] if bounds else False
            mark_top_above_bbox = (
                anchor(glyph, "mark_top").y > bounds[3] if bounds else False
            )
            mark_top_below_bbox = (
                anchor(glyph, "mark_top").y < bounds[3] if bounds else False
            )

            x = anchor(glyph, "mark_top").x
            y = anchor(glyph, "top").y

            # decisions...

            # .el
            if el:
                if wide:
                    y = anchor(glyph, "mark_top").y

                else:
                    y = max(
                        anchor(glyph, "top").y,
                        anchor(glyph, "mark_top").y,
                    )

            # .swsh
            elif swsh:

                base_glyph = self.get_base_glyph(glyph)
                base_glyph_bounds = get_bounds(base_glyph, self.glyphset())

                if VERBOSE:
                    print(glyph, base_glyph)

                base_glyph_top_above_bbox = (
                    anchor(base_glyph, "top").y > base_glyph_bounds[3]
                    if base_glyph_bounds
                    else False
                )
                base_glyph_mark_top_below_bbox = (
                    anchor(base_glyph, "mark_top").y < base_glyph_bounds[3]
                    if base_glyph_bounds
                    else False
                )

                # seen-ar.swsh
                if top_and_mark_top_wide_apart_horizontally:
                    y = anchor(glyph, "mark_top").y

                    if VERBOSE:
                        print("set y to mark_top at 1", glyph)

                # lam-ar.swsh
                elif (
                    anchor(base_glyph, "top")
                    and anchor(base_glyph, "mark_top")
                    and base_glyph_top_above_bbox
                    and base_glyph_mark_top_below_bbox
                ):
                    y = anchor(glyph, "mark_top").y

                    if VERBOSE:
                        print("set y to mark_top at 2", glyph)

                # # alefMaksura-ar.swsh
                # elif not top_above_bbox and not mark_top_above_bbox:
                else:
                    y = max(
                        anchor(glyph, "top").y,
                        anchor(glyph, "mark_top").y,
                    )

                    if VERBOSE:
                        print("set y to max at 2", glyph)

            else:
                # if mark_top_above_bbox:

                y = max(
                    anchor(glyph, "top").y,
                    anchor(glyph, "mark_top").y,
                )

                if VERBOSE:
                    print("set y to max at 3", glyph)

            # # mark_top is too far from top
            # # make them equal
            # if (
            #     abs(anchor(glyph, "top").x - anchor(glyph, "mark_top").x)
            #     > 100
            # ):
            #     x = anchor(glyph, "mark_top").x
            #     y = anchor(glyph, "mark_top").y

            # Top margin
            if bounds:
                if (normal or (el and narrow)) and mark_top_above_bbox:  # swsh or

                    top_margin = 50
                    if swsh:
                        top_margin = 150

                    y = max(
                        y,
                        bounds[3] + top_margin,
                    )

                    if VERBOSE:
                        print("applied top_margin", glyph)

            # meem-ar.conn-mf-center
            # kashidajoiner
            else:
                y = max(
                    anchor(glyph, "top").y,
                    anchor(glyph, "mark_top").y,
                )

                if VERBOSE:
                    print("set y to max at 4", glyph)

            # apply...
            if x != anchor(glyph, "top").x or y != anchor(glyph, "top").y:
                anchor(glyph, "top").x = x
                anchor(glyph, "top").y = y
                modified = True

        # BOTTOM
        if anchor(glyph, "bottom") and anchor(glyph, "mark_bottom"):
            anchor(glyph, "bottom").x = anchor(glyph, "mark_bottom").x

            if (swsh or el) and wide:
                anchor(glyph, "bottom").y = anchor(glyph, "mark_bottom").y
            else:
                anchor(glyph, "bottom").y = min(
                    anchor(glyph, "bottom").y,
                    anchor(glyph, "mark_bottom").y,
                )

            if el and narrow:
                anchor(glyph, "bottom").y = min(
                    anchor(glyph, "bottom").y,
                    anchor(glyph, "mark_bottom").y,
                    bounds[1] - 100,
                )

            modified = True

        # Adjust anchor.y where topthreedots acnhor exists.
        # TODO: make this work for top* instead of just topthreedots
        if (
            anchor(glyph, "topthreedots")
            and len(glyph.components) >= 2
            and anchor(
                self.context.font[glyph.components[1].baseGlyph], "_topthreedots"
            )
        ):
            anchor(glyph, "top").x = anchor(glyph, "topthreedots").x
            anchor(glyph, "top").y += (
                anchor(self.context.font[glyph.components[1].baseGlyph], "top").y
                - anchor(self.context.font[glyph.components[1].baseGlyph], "_top").y
                - 150
            )

        # # Ligatures
        # if glyph.components:
        #     for i in range(len(glyph.components)):

        #         if anchor(glyph, f"top_{i+1}") and anchor(
        #             glyph, f"mark_top_{i+1}"
        #         ):
        #             anchor(glyph, f"top_{i+1}").x = anchor(
        #                 glyph, f"mark_top_{i+1}"
        #             ).x
        #             anchor(glyph, f"top_{i+1}").y = anchor(
        #                 glyph, f"mark_top_{i+1}"
        #             ).y
        #             modified = True

        #         if anchor(glyph, f"bottom_{i+1}") and anchor(
        #             glyph, f"mark_bottom_{i+1}"
        #         ):
        #             anchor(glyph, f"bottom_{i+1}").x = anchor(
        #                 glyph, f"mark_bottom_{i+1}"
        #             ).x
        #             anchor(glyph, f"bottom_{i+1}").y = anchor(
        #                 glyph, f"mark_bottom_{i+1}"
        #             ).y
        #             modified = True

        return modified
