#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
#  FreeType high-level python API - Copyright 2011 Nicolas P. Rougier
#  Distributed under the terms of the new BSD license.
#
# -----------------------------------------------------------------------------
# sudo pip install freetype-py
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

def text_extents(face, text):
    slot = face.glyph
    width, height, baseline = 0, 0, 0
    previous = 0
    for i,c in enumerate(text):
        face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        bitmap = slot.bitmap
        height = max(height,
                     bitmap.rows + max(0,-(slot.bitmap_top-bitmap.rows)))
        baseline = max(baseline, max(0,-(slot.bitmap_top-bitmap.rows)))
        kerning = face.get_kerning(previous, c)
        width += (slot.advance.x >> 6) + (kerning.x >> 6)
        previous = c
    return (width, height, baseline)

def bitblt(src, dst, src_w, src_h, dst_w, dst_h, dst_x, dst_y):
    for x in range(src_w):
        for y in range(src_h):
            dst[(dst_y + y) * dst_w + dst_x + x] = src[y * src_w + x]

def text_render(face, width, height, baseline, text,):
    Z = [0] * (width * height)
    slot = face.glyph
    x, y = 0, 0
    previous = 0
    for c in text:
        face.load_char(c, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_TARGET_MONO)
        bitmap = slot.bitmap
        unpacked_bmp = unpack_mono_bitmap(bitmap)
        # print bitmap.buffer, 'unpacked:', unpacked_bmp, len(unpacked_bmp)
        top = slot.bitmap_top
        left = slot.bitmap_left
        w,h = bitmap.width, bitmap.rows
        y = height-baseline-top
        kerning = face.get_kerning(previous, c)
        x += (kerning.x >> 6)
        print 'Glyph "%s" width=%i height=%i blt_x=%i blt_y=%i' % (c, w, h, x, y)
        # print_bitmap(unpacked_bmp, w, h)
        bitblt(unpacked_bmp, Z, w, h, width, height, x, y)
        # print_bitmap(Z, width, height)
        x += (slot.advance.x >> 6)
        previous = c
        # print '\n\n'
    return Z

def print_bitmap(bmp, width, height):
    for i in range(height):
        rowstr = ''
        for j in range(width):
            rowstr += '#' if bmp[i*width+j] else ' '
        print rowstr

if __name__ == '__main__':
    face = freetype.Face('/Users/daniel/dev/github/piradio/test-apps/font4.ttf')
    text = u'one, two, three'
    face.set_char_size( 20*64 )

    width, height, baseline = text_extents(face, text)
    text_bmp = text_render(face, width, height, baseline, text)

    print '"%s": width=%i height=%i baseline=%i' % (text, width, height, baseline)
    print_bitmap(text_bmp, width, height)