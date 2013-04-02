import graphics
import commons

class Widget(object):
    def __init__(self, bounds, parent=None):
        self.bounds = bounds
        self.parent = None
        self.children = []

    def paint(self):
        [child.paint() for child in self.children]

# Label, List, Root

def render_list(surface, x, y, font, items, selected_index=-1, minheight=-1, maxvisible=4):
    maxheight = max([font.text_extents(text)[1] for text in items])
    maxheight = max(minheight, maxheight)
    start = max(0, min(selected_index-maxvisible+1, len(items)-maxvisible))
    end = start + maxvisible
    selected_index -= start
    for i, text in enumerate(items[start:end]):
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        if i == selected_index:
            for i in range(y,y+maxheight):
                surface.hline(i)
        top_offset = (maxheight - textheight) / 2
        surface.bitblt(textbitmap, x, y+top_offset, op=graphics.rop_xor)
        y += maxheight

def render_progressbar(surface, x, y, w, h, progress):
    surface.strokerect(x, y, w, h)
    surface.fillrect(x + 2, y + 2, int((w-4) * commons.clamp(progress, 0, 1)), h - 4)

def render_static_list(surface, x, y, font, items, minheight=-1, maxvisible=4):
    maxheight = max([font.text_extents(text)[1] for text in items])
    maxheight = max(minheight, maxheight)
    start = max(0, min(maxvisible+1, len(items)-maxvisible))
    end = start + maxvisible
    for i, text in enumerate(items[start:end]):
        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        top_offset = (maxheight - textheight) / 2
        surface.bitblt(textbitmap, x, y+top_offset, op=graphics.rop_xor)
        y += maxheight

if __name__ == '__main__':
    s = graphics.Surface(64, 20)
    render_progressbar(s, 2, 2, 50, 16, -1)
    print repr(s)
    render_progressbar(s, 2, 2, 50, 16, 0.5)
    print repr(s)
    render_progressbar(s, 2, 2, 50, 16, 0.9)
    print repr(s)
    render_progressbar(s, 2, 2, 50, 16, 10)
    print repr(s)
