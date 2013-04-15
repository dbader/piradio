import graphics
import commons


def render_list(surface, x, y, font, items, selected_index=-1, minheight=-1, maxvisible=4):
    maxheight = max(font.text_extents(text)[1] for text in items)
    maxheight = max(minheight, maxheight)

    start = max(0, min(selected_index-maxvisible+1, len(items)-maxvisible))
    end = start + maxvisible
    selected_index -= start

    for i, text in enumerate(items[start:end]):
        if i == selected_index:
            surface.fillrect(0, y, surface.width, maxheight)

        textwidth, textheight, baseline = font.text_extents(text)
        textbitmap = font.render(text, width=textwidth, height=textheight, baseline=baseline)
        top_offset = (maxheight - textheight + baseline) / 2
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

    import fontlib
    f = fontlib.Font('assets/font.ttf', 8)
    surf = graphics.Surface(128, 32)

    render_list(surf, 0, 0, f, ['B5 Aktuell', 'Bob Marley Radio', 'thry', 'four', 'five', 'six', 'seven', 'eight'], 0, 11, 3)
    print repr(surf)

    surf.clear()
    render_list(surf, 0, 0, f, ['B5 Aktuell', 'Bob Marley Radio', 'thry', 'four', 'five', 'six', 'seven', 'eight'], 1, 11, 3)
    print repr(surf)

    #
    #
    # f = fontlib.Font('assets/font.ttf', 8)
    # surf = graphics.Surface(128, 64)
    # def benchmark():
    #     for i in xrange(1000):
    #         render_list(surf, 0, 0, f, ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight'])
    # import cProfile
    # import pstats
    # cProfile.run('benchmark()', 'uibench.profile')
    # p = pstats.Stats('uibench.profile')
    # print p.sort_stats('cumulative').print_stats(20)
    # print p.sort_stats('time').print_stats(20)
