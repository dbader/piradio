import graphics

class Widget(object):
    def __init__(self, bounds, parent=None):
        self.bounds = bounds
        self.parent = None
        self.children = []

    def paint(self):
        [child.paint() for child in self.children]

# Label, List, Root

def render_list(framebuffer, x, y, font, items, selected_index=-1, minheight=-1, maxvisible=4):
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
                framebuffer.hline(i)
        top_offset = (maxheight - textheight) / 2
        framebuffer.bitblt(textbitmap, x, y+top_offset, op=graphics.rop_xor)
        y += maxheight
