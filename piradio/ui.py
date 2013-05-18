import piradio.graphics as graphics
import piradio.commons as commons


def render_list(surface, x, y, font, items,
                selected_index=-1, minheight=-1, maxvisible=4):
    """Draw a list widget with selectable items into the given surface."""
    maxheight = max(font.text_extents(text)[1] for text in items)
    maxheight = max(minheight, maxheight)

    start = max(0, min(selected_index - maxvisible + 1,
                       len(items) - maxvisible))
    end = start + maxvisible
    selected_index -= start

    for i, text in enumerate(items[start:end]):
        if i == selected_index:
            surface.fillrect(0, y, surface.width, maxheight)

        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight,
                                 baseline=baseline)
        top_offset = (maxheight - textheight + baseline) / 2
        surface.bitblt(textbitmap, x, y + top_offset, op=graphics.rop_xor)

        y += maxheight


def render_static_list(surface, x, y, font, items, minheight=-1, maxvisible=4):
    """Draw a static (non-selectable) list into the given surface."""
    maxheight = max([font.text_extents(text)[1] for text in items])
    maxheight = max(minheight, maxheight)
    start = max(0, min(maxvisible + 1, len(items) - maxvisible))
    end = start + maxvisible
    for text in items[start:end]:
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight,
                                 baseline=baseline)
        top_offset = (maxheight - textheight) / 2
        surface.bitblt(textbitmap, x, y + top_offset, op=graphics.rop_xor)
        y += maxheight


def render_progressbar(surface, x, y, w, h, progress):
    """Draw a progress bar widget into the given surface."""
    surface.strokerect(x, y, w, h)
    bar_width = int((w - 4) * commons.clamp(progress, 0, 1))
    surface.fillrect(x + 2, y + 2, bar_width, h - 4)
