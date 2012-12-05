#!/usr/bin/env python
# -*- coding: utf-8 -*-
import freetype

def bits(x):
    """Unpack the bits of am 8bit word into a list."""
    data = []
    for i in range(8):
        data.insert(0, int((x & 1) == 1))
        x = x >> 1
    return data

def unpack_mono_bitmap(bitmap):
    """Unpack a freetype FT_LOAD_TARGET_MONO bitmap into a list that has one element per pixel."""
    data = []
    for i in range(bitmap.rows):
        row = []
        for j in range(bitmap.pitch):
            row.extend(bits(bitmap.buffer[i*bitmap.pitch+j]))
        data.extend(row[:bitmap.width])
    return data
    
def bitblt(src, dst, src_w, src_h, dst_w, dst_h, dst_x, dst_y):
    for x in range(src_w):
        for y in range(src_h):
            dst[(dst_y + y) * dst_w + dst_x + x] = src[y * src_w + x]
            
def bitmap2str(bmp, width, height, filled_char= '#', empty_char=' '):
    bstr = ''
    for i in range(height):
        rowstr = ''
        for j in range(width):
            rowstr += filled_char if bmp[i*width+j] else empty_char
        bstr += rowstr + '\n'
    return bstr

class Font(object):
    def __init__(self, filename, size):
        self._face = freetype.Face(filename)
        self.set_size(size)
        self._glyphcache = {}
      
    # @property
    # def size(self):
    #     """The font's size in pixels."""
    #     return self.thesize
       
    # @size.setter 
    def set_size(self, size):
        """Set the font's size in pixels."""
        self._face.set_pixel_sizes(size, size)
        self._glyphcache = {}
        # self.thesize = size   
        
    def _get_glyph(self, c):
        cached_glyph = self._glyphcache.get(c)
        cached_glyph = None
        if cached_glyph:
            return cached_glyph            
        self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        glyph = self._face.glyph
        bitmap = glyph.bitmap
        unpacked_bmp = unpack_mono_bitmap(bitmap)        
        top = glyph.bitmap_top
        left = glyph.bitmap_left
        w,h = bitmap.width, bitmap.rows        
        # print c,top,left,w,h
        self._glyphcache[c] = (w, h, top, left, unpacked_bmp)
        return w, h, top, left, unpacked_bmp
        
    def text_extents(self, text):
        """Return (width, height, baseline) of `text` rendered in the current font."""
        slot = self._face.glyph
        width, height, baseline = 0, 0, 0
        previous = 0
        for c in text:
            self._face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
            bitmap = slot.bitmap
            height = max(height, bitmap.rows + max (0, -(slot.bitmap_top - bitmap.rows)))
            baseline = max(baseline, max(0, -(slot.bitmap_top - bitmap.rows)))
            kerning = self._face.get_kerning(previous, c)
            width += (slot.advance.x >> 6) + (kerning.x >> 6)
            previous = c
        return (width, height+baseline, baseline)
        
    def render(self, text, width=None, height=None, baseline=None):
        if width is None or height is None or baseline is None:
            width, height, baseline = self.text_extents(text)
        outbuffer = [0] * (width * height)
        slot = self._face.glyph
        x, y = 0, 0
        previous = 0
        for c in text:
            w, h, top, left, unpacked_bmp = self._get_glyph(c)
            y = height-baseline-top
            # print height, baseline, top
            kerning = self._face.get_kerning(previous, c)
            x += (kerning.x >> 6)
            # print 'render',c,w,h,x,y
            # print bitmap2str(unpacked_bmp, w, h)
            bitblt(unpacked_bmp, outbuffer, w, h, width, height, x, y)
            # print bitmap2str(outbuffer, width, height)
            x += (slot.advance.x >> 6)
            previous = c
        return outbuffer
            
if __name__ == '__main__':
    f = Font('/Users/daniel/dev/piradio/test-apps/HARDKAZE.ttf', 16)
    text = u'one, two, three'
    # text = 'T,'
    width, height, baseline = f.text_extents(text)
    print '"%s": width=%i height=%i baseline=%i' % (text, width, height, baseline)
    print bitmap2str(f.render(text), width, height)
    
    def benchmark():
        for i in range(100):
            f.render('Hello, World.')
    
    # import cProfile
    # import pstats
    # cProfile.run('benchmark()', 'fontbench.profile')
    # p = pstats.Stats('fontbench.profile')
    # print p.sort_stats('cumulative').print_stats(20)
    # print p.sort_stats('time').print_stats(20)