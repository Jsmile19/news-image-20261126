#!/usr/bin/env python3
"""Draw the news of 26 November 2026 using ctypes, Cairo and no packages.

All reporting is supplied in the build brief. No network or external artwork
is used. Coordinates, text and colours are fixed for reproducible rendering.
"""

import ctypes as C
import ctypes.util
import math
from pathlib import Path


WIDTH = HEIGHT = 1024
OUT = Path(__file__).resolve().with_name('entry.png')
cairo = C.CDLL(ctypes.util.find_library('cairo') or 'libcairo.so.2')


def bind(name, result, *args):
    function = getattr(cairo, name)
    function.restype = result
    function.argtypes = list(args)
    return function


P = C.c_void_p
D = C.c_double
I = C.c_int
surface_create = bind('cairo_image_surface_create', P, I, I, I)
create = bind('cairo_create', P, P)
destroy = bind('cairo_destroy', None, P)
surface_destroy = bind('cairo_surface_destroy', None, P)
write_png = bind('cairo_surface_write_to_png', I, P, C.c_char_p)
status = bind('cairo_status', I, P)
rgb = bind('cairo_set_source_rgb', None, P, D, D, D)
paint = bind('cairo_paint', None, P)
rectangle = bind('cairo_rectangle', None, P, D, D, D, D)
fill = bind('cairo_fill', None, P)
stroke = bind('cairo_stroke', None, P)
new_path = bind('cairo_new_path', None, P)
move = bind('cairo_move_to', None, P, D, D)
line_to = bind('cairo_line_to', None, P, D, D)
close = bind('cairo_close_path', None, P)
line_width = bind('cairo_set_line_width', None, P, D)
line_cap = bind('cairo_set_line_cap', None, P, I)
arc = bind('cairo_arc', None, P, D, D, D, D, D)
select_font = bind('cairo_select_font_face', None, P, C.c_char_p, I, I)
font_size = bind('cairo_set_font_size', None, P, D)
show_text = bind('cairo_show_text', None, P, C.c_char_p)
save = bind('cairo_save', None, P)
restore = bind('cairo_restore', None, P)
translate = bind('cairo_translate', None, P, D, D)
scale = bind('cairo_scale', None, P, D, D)


class Extents(C.Structure):
    _fields_ = [(key, D) for key in (
        'x_bearing', 'y_bearing', 'width', 'height', 'x_advance', 'y_advance'
    )]


text_extents = bind('cairo_text_extents', None, P, C.c_char_p, C.POINTER(Extents))
surface = surface_create(1, WIDTH, HEIGHT)  # CAIRO_FORMAT_RGB24
ctx = create(surface)
INK = '#182b31'
PAPER = '#f3efe4'
RED = '#c44730'
TEAL = '#42686c'
MUTED = '#526164'
RULE = '#bbc0b6'
WHITE = '#fffaf0'
SANS = 'DejaVu Sans'
CONDENSED = 'Nimbus Sans Narrow'
SERIF = 'DejaVu Serif'


def color(value):
    value = value.lstrip('#')
    rgb(ctx, *(int(value[i:i + 2], 16) / 255 for i in (0, 2, 4)))


def box(x, y, w, h, tint):
    new_path(ctx)
    color(tint)
    rectangle(ctx, x, y, w, h)
    fill(ctx)


def path(points, tint=INK, width=2, closed=False, solid=False):
    new_path(ctx)
    color(tint)
    line_width(ctx, width)
    move(ctx, *points[0])
    for point in points[1:]:
        line_to(ctx, *point)
    if closed:
        close(ctx)
    (fill if solid else stroke)(ctx)


def circle(x, y, radius, tint=INK, solid=False, width=2):
    new_path(ctx)
    color(tint)
    line_width(ctx, width)
    arc(ctx, x, y, radius, 0, math.tau)
    (fill if solid else stroke)(ctx)


def text(value, x, baseline, size, tint=INK, bold=False,
         family=SANS, max_width=None):
    select_font(ctx, family.encode(), 0, int(bold))
    font_size(ctx, size)
    extent = Extents()
    text_extents(ctx, value.encode(), C.byref(extent))
    if max_width is not None and extent.x_advance > max_width:
        raise ValueError(f'Text exceeds {max_width}px: {value!r} '
                         f'({extent.x_advance:.1f}px)')
    if x + extent.x_bearing < 0 or x + extent.x_bearing + extent.width > WIDTH:
        raise ValueError(f'Text exceeds canvas width: {value!r}')
    if baseline + extent.y_bearing < 0 or baseline + extent.y_bearing + extent.height > HEIGHT:
        raise ValueError(f'Text exceeds canvas height: {value!r}')
    color(tint)
    move(ctx, x, baseline)
    show_text(ctx, value.encode())
    return extent.x_advance


def lines(values, x, baseline, size, leading, **kwargs):
    for i, value in enumerate(values):
        text(value, x, baseline + i * leading, size, **kwargs)


def icon(kind, x, y):
    """Small original line drawings; each fits a 52 x 46 box."""
    save(ctx)
    translate(ctx, x, y)
    line_cap(ctx, 1)
    if kind == 'ship':
        path([(3, 28), (48, 28), (39, 39), (12, 39), (3, 28)], TEAL, 2)
        path([(14, 27), (14, 14), (33, 14), (33, 27)], TEAL, 2)
        path([(24, 14), (24, 4), (34, 4)], TEAL, 2)
        for px in (2, 20, 38):
            path([(px, 44), (px + 5, 42), (px + 10, 44)], TEAL, 1.7)
        path([(2, 4), (12, 14)], RED, 3)
        path([(8, 5), (12, 14), (3, 10)], RED, 2)
    elif kind == 'atom':
        circle(26, 23, 4, RED, True)
        for angle in (0, math.pi / 3, -math.pi / 3):
            points = []
            for n in range(49):
                t = math.tau * n / 48
                px, py = 23 * math.cos(t), 8 * math.sin(t)
                points.append((26 + px * math.cos(angle) - py * math.sin(angle),
                               23 + px * math.sin(angle) + py * math.cos(angle)))
            path(points, TEAL, 1.8)
    elif kind == 'eu':
        for i in range(12):
            angle = math.tau * i / 12 - math.pi / 2
            cx, cy = 26 + 19 * math.cos(angle), 23 + 19 * math.sin(angle)
            pts = []
            for j in range(10):
                a = math.tau * j / 10 - math.pi / 2
                r = 2.6 if j % 2 == 0 else 1.15
                pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
            path(pts, TEAL, closed=True, solid=True)
        path([(18, 23), (23, 28), (34, 17)], RED, 2.5)
    elif kind == 'virus':
        circle(26, 23, 13, TEAL, width=2.1)
        for i in range(8):
            a = i * math.tau / 8
            p = [(26 + r * math.cos(a), 23 + r * math.sin(a)) for r in (14, 21)]
            path(p, TEAL, 2)
            circle(*p[-1], 2, TEAL, True)
        for px, py in ((21, 19), (31, 22), (24, 29)):
            circle(px, py, 2, RED, True)
    elif kind == 'building':
        path([(9, 34), (9, 4), (40, 4), (40, 28)], TEAL, 2)
        path([(28, 4), (23, 15), (30, 21), (23, 32)], RED, 2.5)
        for px, py in ((15, 11), (34, 11), (15, 22)):
            box(px, py, 4, 5, TEAL)
        path([(3, 42), (12, 33), (23, 40), (33, 30), (48, 42)], TEAL, 2)
        path([(3, 44), (49, 44)], TEAL, 2)
    elif kind == 'budget':
        for px, h in ((5, 13), (18, 22), (31, 34)):
            box(px, 43 - h, 8, h, TEAL)
        path([(5, 20), (20, 10), (35, 1), (47, 1)], RED, 2.5)
        path([(40, 0), (47, 1), (44, 8)], RED, 2)
    restore(ctx)


def panel(x, y, category, heading, summary, kind, headline_size=27):
    width = 304
    box(x, y, width, 3, INK)
    text(category, x, y + 26, 13, RED, True, max_width=240)
    icon(kind, x + 248, y + 5)
    lines(heading, x, y + 73, headline_size, 29, bold=True,
          family=CONDENSED, max_width=width)
    lines(summary, x, y + 169, 18, 24, max_width=width)


# A restrained newspaper palette and an explicit date for a news-blind judge.
color(PAPER)
paint(ctx)
box(32, 26, 38, 5, RED)
text('THE DAILY NEWS POSTER', 82, 34, 13, RED, True)
text('WORLD EDITION', 854, 34, 13, MUTED, True, max_width=138)
text('THE WORLD IN ONE PICTURE', 29, 94, 61, INK, True,
     family=CONDENSED, max_width=966)
box(32, 110, 960, 2, INK)
text('THURSDAY', 34, 148, 19, INK, True)
text('26 November 2026', 214, 151, 37, INK, True, max_width=634)
text('A DAY IN HEADLINES', 830, 146, 13, MUTED, True, max_width=162)

# The lead dominates both in area and type size.
box(32, 174, 960, 246, INK)
box(32, 174, 7, 246, RED)
text('LEAD STORY  /  GAZA', 52, 202, 14, '#e9a58b', True)
lines(['ISRAELI STRIKE', 'KILLS NINE IN GAZA'], 50, 259, 59, 61,
      tint=WHITE, bold=True, family=CONDENSED, max_width=627)
lines(['Nine people killed, including Hamas’s', 'deputy education minister.'],
      53, 362, 22, 30, tint=WHITE, max_width=626)

# Abstract city and rubble: a drawn illustration, with no photographic content.
save(ctx)
translate(ctx, 713, 211)
circle(138, 57, 49, '#3c4b4e', True)
for px, py, w, h in ((5, 73, 34, 82), (44, 50, 36, 105),
                     (85, 89, 31, 66), (166, 66, 38, 89), (208, 99, 35, 56)):
    box(px, py, w, h, '#75827e')
    for wx in range(int(px + 8), int(px + w - 4), 13):
        for wy in range(int(py + 11), 143, 19):
            box(wx, wy, 5, 8, INK)
path([(111, 151), (111, 87), (131, 98), (144, 74), (160, 92),
      (157, 155)], '#c0c4b8', closed=True, solid=True)
path([(121, 118), (134, 107), (147, 118), (141, 136)], INK, 3)
for pts in ([(0, 169), (29, 146), (52, 169)],
            [(48, 169), (82, 144), (101, 169)],
            [(91, 169), (127, 145), (156, 169)],
            [(147, 169), (180, 147), (208, 169)],
            [(199, 169), (224, 151), (248, 169)]):
    path(pts, '#c0c4b8', closed=True, solid=True)
path([(6, 177), (246, 177)], '#c0c4b8', 2)
for pts in ([(106, 34), (91, 13)], [(135, 25), (135, 0)],
            [(162, 32), (179, 11)], [(180, 51), (203, 43)]):
    path(pts, '#e9a58b', 3)
restore(ctx)

# Six supporting stories, in a native newspaper-style 3 x 2 grid.
panel(32, 446, '01 / UKRAINE',
      ['RUSSIAN MISSILES HIT', 'KYIV & A GRAIN SHIP'],
      ['7 injured by a ballistic missile;', 'grain ship hit near Odesa.'], 'ship', 27)
panel(360, 446, '02 / NORTH KOREA',
      ['PYONGYANG SIGNALS', 'NUCLEAR EXPANSION'],
      ['Signals plans to expand its', 'nuclear weapons programme.'], 'atom', 27)
panel(688, 446, '03 / EUROPEAN UNION',
      ['EU LEADERS BARGAIN', 'IN BRUSSELS'],
      ['Budget negotiations and more', 'funding for Ukraine.'], 'eu', 27)
panel(32, 680, '04 / GLOBAL HEALTH',
      ['WHO FLAGS NEW', 'COVID VARIANT'],
      ['World Health Organization', 'flags a variant for monitoring.'], 'virus', 29)
panel(360, 680, '05 / PAKISTAN',
      ['KARACHI BUILDING', 'COLLAPSES'],
      ['4 people killed;', '17 still missing.'], 'building', 29)
panel(688, 680, '06 / RUSSIA',
      ['BIGGEST MILITARY', 'BUDGET SINCE USSR'],
      ['Moscow’s military spending:', 'largest since the Soviet era.'], 'budget', 28)

# One continuous bottom ticker: four concise extras, each separated by a dot.
box(32, 918, 960, 76, INK)
text('ALSO TODAY', 47, 940, 12, '#e9a58b', True)
ticker = ('MACY’S 100TH THANKSGIVING PARADE, NYC • '
          'EUROSTAR PARIS–LONDON CANCELLED: STRIKE • '
          'RAM PRICES ×3 AS CHIP DEMAND SURGES • GOLD −3%')
text(ticker, 47, 974, 14.5, WHITE, True, family=CONDENSED, max_width=930)

if status(ctx) != 0:
    raise RuntimeError(f'Cairo drawing failed with status {status(ctx)}')
result = write_png(surface, str(OUT).encode())
destroy(ctx)
surface_destroy(surface)
if result != 0:
    raise RuntimeError(f'Cairo PNG write failed with status {result}')
if OUT.stat().st_size > 1048576:
    raise RuntimeError('PNG exceeds the 1 MiB limit')
print(f'{OUT}: {WIDTH} x {HEIGHT}, {OUT.stat().st_size} bytes')
