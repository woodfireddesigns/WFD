"""Minimal drafting primitives on top of reportlab."""
import math
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfgen import canvas

INK    = HexColor("#1b1b1b")
LINE   = HexColor("#2b2b2b")
THIN   = HexColor("#7a7a7a")
DIMC   = HexColor("#0f6b4f")
NOTE   = HexColor("#8a3b12")
ACCENT = HexColor("#2f4f34")
FILL   = HexColor("#e9e2d4")
FILL2  = HexColor("#d8ccb4")
GRID   = HexColor("#e4e0d6")
RED    = HexColor("#a3231b")

def frac(x, den=16):
    """Decimal inches -> feet/inch/fraction string."""
    neg = x < 0; x = abs(x)
    ft = int(x // 12); inch = x - ft*12
    whole = int(inch); f = round((inch - whole)*den)
    if f == den: whole += 1; f = 0
    if whole == 12: ft += 1; whole = 0
    from math import gcd
    s = ""
    if ft: s += f'{ft}\'-'
    if f:
        g = gcd(f, den)
        s += f'{whole}-{f//g}/{den//g}"' if whole or ft else f'{f//g}/{den//g}"'
    else:
        s += f'{whole}"'
    return ("-" if neg else "") + s

class Sheet:
    def __init__(self, c, W, H, num, title, sub="", scale=""):
        self.c, self.W, self.H = c, W, H
        self.num, self.title, self.sub, self.scale = num, title, sub, scale
        self.ox = self.oy = 0.0; self.k = 1.0
    # ---- viewport -----------------------------------------------------
    def view(self, x0, y0, w, h, minx, miny, maxx, maxy, pad=0.06):
        sx = w/max(maxx-minx, 1e-6); sy = h/max(maxy-miny, 1e-6)
        self.k = min(sx, sy)*(1-pad)
        cw, ch = (maxx-minx)*self.k, (maxy-miny)*self.k
        self.ox = x0 + (w-cw)/2 - minx*self.k
        self.oy = y0 + (h-ch)/2 - miny*self.k
        return self.k
    def P(self, x, y): return (self.ox + x*self.k, self.oy + y*self.k)
    # ---- primitives ---------------------------------------------------
    def line(self, p0, p1, col=LINE, w=0.9, dash=None):
        c = self.c; c.saveState(); c.setStrokeColor(col); c.setLineWidth(w)
        if dash: c.setDash(dash)
        c.line(*self.P(*p0), *self.P(*p1)); c.restoreState()
    def rline(self, p0, p1, col=LINE, w=0.9, dash=None):
        c = self.c; c.saveState(); c.setStrokeColor(col); c.setLineWidth(w)
        if dash: c.setDash(dash)
        c.line(p0[0], p0[1], p1[0], p1[1]); c.restoreState()
    def poly(self, pts, fill=None, stroke=LINE, w=1.0, close=True, dash=None):
        c = self.c; c.saveState()
        if dash: c.setDash(dash)
        p = c.beginPath(); a = self.P(*pts[0]); p.moveTo(*a)
        for q in pts[1:]: p.lineTo(*self.P(*q))
        if close: p.close()
        if fill: c.setFillColor(fill)
        c.setStrokeColor(stroke or LINE); c.setLineWidth(w)
        c.drawPath(p, stroke=1 if stroke else 0, fill=1 if fill else 0); c.restoreState()
    def circle(self, cen, r, fill=None, stroke=LINE, w=0.9):
        c = self.c; c.saveState(); c.setStrokeColor(stroke or LINE); c.setLineWidth(w)
        if fill: c.setFillColor(fill)
        x, y = self.P(*cen); c.circle(x, y, r*self.k, stroke=1 if stroke else 0, fill=1 if fill else 0)
        c.restoreState()
    def arc_seg(self, cen, r, a0, a1, col=LINE, w=1.0, n=48):
        pts = [(cen[0]+r*math.cos(math.radians(a0+(a1-a0)*i/n)),
                cen[1]+r*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]
        for i in range(n): self.line(pts[i], pts[i+1], col, w)
    def txt(self, p, s, size=6.2, col=INK, anchor="l", bold=False, rot=0, model=True):
        c = self.c; c.saveState(); c.setFillColor(col)
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        x, y = self.P(*p) if model else p
        c.translate(x, y); c.rotate(rot)
        {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[anchor](0, 0, s)
        c.restoreState()
    def tick(self, p, r=2.2, col=DIMC):
        x, y = self.P(*p); self.rline((x-r, y-r), (x+r, y+r), col, 0.9)
    # ---- dimensions ---------------------------------------------------
    def dim(self, p0, p1, off=0.0, label=None, col=DIMC, size=5.8, flip=False, ext=True):
        (x0, y0), (x1, y1) = p0, p1
        L = math.hypot(x1-x0, y1-y0)
        if L < 1e-6: return
        d = ((x1-x0)/L, (y1-y0)/L); n = (-d[1], d[0])
        if flip: n = (-n[0], -n[1])
        a = (x0+n[0]*off, y0+n[1]*off); b = (x1+n[0]*off, y1+n[1]*off)
        self.line(a, b, col, 0.7)
        if ext:
            self.line(p0, (x0+n[0]*off*1.12, y0+n[1]*off*1.12), col, 0.4)
            self.line(p1, (x1+n[0]*off*1.12, y1+n[1]*off*1.12), col, 0.4)
        self.tick(a); self.tick(b)
        m = ((a[0]+b[0])/2, (a[1]+b[1])/2)
        ang = math.degrees(math.atan2(d[1], d[0]))
        if ang > 90 or ang <= -90: ang += 180
        mx, my = self.P(*m)
        self.c.saveState(); self.c.setFillColor(col)
        self.c.setFont("Helvetica-Bold", size); self.c.translate(mx, my); self.c.rotate(ang)
        self.c.setFillColor(HexColor("#fbfaf6"))
        s = label or frac(L); wt = self.c.stringWidth(s, "Helvetica-Bold", size)
        self.c.rect(-wt/2-1.5, -1.6, wt+3, size+0.4, stroke=0, fill=1)
        self.c.setFillColor(col); self.c.drawCentredString(0, 0, s)
        self.c.restoreState()
    def leader(self, p, dxy, s, size=5.6, col=NOTE, anchor="l"):
        x, y = self.P(*p); ex, ey = x+dxy[0], y+dxy[1]
        self.rline((x, y), (ex, ey), col, 0.6)
        self.rline((ex, ey), (ex + (10 if anchor == "l" else -10), ey), col, 0.6)
        self.c.saveState(); self.c.setFillColor(col); self.c.setFont("Helvetica", size)
        (self.c.drawString if anchor == "l" else self.c.drawRightString)(
            ex + (13 if anchor == "l" else -13), ey-1.8, s)
        self.c.restoreState()
        self.c.saveState(); self.c.setFillColor(col); self.c.circle(x, y, 1.3, stroke=0, fill=1); self.c.restoreState()
    def bubble(self, p, s, r=7.0):
        x, y = p; c = self.c; c.saveState()
        c.setFillColor(HexColor("#fbfaf6")); c.setStrokeColor(INK); c.setLineWidth(0.9)
        c.circle(x, y, r, stroke=1, fill=1); c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7.2); c.drawCentredString(x, y-2.5, s); c.restoreState()

def block(c, x, y_top, width, lines, y_min=78, size=7.6, lead=11.0, title=None, tcol=None):
    """Bullet/notes block that auto-shrinks its leading to fit above y_min.
    A line that is ALL CAPS becomes a bold sub-heading. Lines are wrapped to width."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    def wrap(s, fs):
        if not s: return [""]
        ind = "  " if s.startswith(("·", "-", "*")) else ""
        out, cur = [], ""
        for w in s.split(" "):
            t = (cur + " " + w).strip()
            if stringWidth(t, "Helvetica", fs) <= width or not cur: cur = t
            else: out.append(cur); cur = ind + w
        out.append(cur); return out
    for fs, ld in ((size, lead), (size-0.4, lead-0.9), (size-0.8, lead-1.7), (size-1.1, lead-2.4)):
        flat = []
        for s in lines: flat += [(seg, s.isupper() and bool(s.strip())) for seg in wrap(s, fs)]
        need = (18 if title else 0) + len(flat)*ld
        if y_top - need >= y_min: break
    y = y_top
    if title:
        c.setFont("Helvetica-Bold", min(11, fs+3)); c.setFillColor(tcol or INK)
        c.drawString(x, y, title); y -= 16
    for s, up in flat:
        c.setFont("Helvetica-Bold" if up else "Helvetica", fs)
        c.setFillColor(RED if up and ("NOT" in s or "NEVER" in s or "READ" in s or "WALLS" in s or "GUARDRAIL" in s)
                       else (ACCENT if up else INK))
        c.drawString(x, y, s); y -= ld
    return y
