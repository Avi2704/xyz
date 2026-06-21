#!/usr/bin/env python3
"""Dependency-free renderer for the DipDetectives logo.
Renders to PNG using supersampling for anti-aliasing. No external libs."""
import math, zlib, struct

# ---------------- PNG / Canvas ----------------
class Canvas:
    def __init__(self, w, h, ss=3):
        self.w, self.h, self.ss = w, h, ss
        self.W, self.H = w*ss, h*ss
        self.buf = bytearray(self.W*self.H*4)  # RGBA, transparent

    def _set(self, x, y, c):
        if 0 <= x < self.W and 0 <= y < self.H:
            i = (y*self.W + x)*4
            self.buf[i]=c[0]; self.buf[i+1]=c[1]; self.buf[i+2]=c[2]; self.buf[i+3]=255

    def fill_circle(self, cx, cy, r, c):
        s=self.ss; cx*=s; cy*=s; r*=s
        x0=int(cx-r-1); x1=int(cx+r+1); y0=int(cy-r-1); y1=int(cy+r+1)
        r2=r*r
        for y in range(y0,y1+1):
            dy=y-cy
            for x in range(x0,x1+1):
                dx=x-cx
                if dx*dx+dy*dy<=r2: self._set(x,y,c)

    def capsule(self, x1,y1,x2,y2,width,c):
        s=self.ss; x1*=s;y1*=s;x2*=s;y2*=s; hw=width*s/2.0
        minx=int(min(x1,x2)-hw-1); maxx=int(max(x1,x2)+hw+1)
        miny=int(min(y1,y2)-hw-1); maxy=int(max(y1,y2)+hw+1)
        dx=x2-x1; dy=y2-y1; L2=dx*dx+dy*dy
        hw2=hw*hw
        for y in range(miny,maxy+1):
            for x in range(minx,maxx+1):
                if L2==0:
                    t=0.0
                else:
                    t=((x-x1)*dx+(y-y1)*dy)/L2
                    t=0.0 if t<0 else (1.0 if t>1 else t)
                px=x1+t*dx; py=y1+t*dy
                ddx=x-px; ddy=y-py
                if ddx*ddx+ddy*ddy<=hw2: self._set(x,y,c)

    def polyline(self, pts, width, c):
        for i in range(len(pts)-1):
            self.capsule(pts[i][0],pts[i][1],pts[i+1][0],pts[i+1][1],width,c)

    def fill_poly(self, pts, c):
        s=self.ss
        xs=[p[0]*s for p in pts]; ys=[p[1]*s for p in pts]
        y0=int(min(ys)); y1=int(max(ys)); x0=int(min(xs)); x1=int(max(xs))
        n=len(pts)
        for y in range(y0,y1+1):
            yc=y+0.5
            nodes=[]
            j=n-1
            for i in range(n):
                yi=ys[i]; yj=ys[j]
                if (yi<yc and yj>=yc) or (yj<yc and yi>=yc):
                    nodes.append(xs[i]+(yc-yi)/(yj-yi)*(xs[j]-xs[i]))
                j=i
            nodes.sort()
            for k in range(0,len(nodes)-1,2):
                xa=int(math.ceil(nodes[k]-0.5)); xb=int(math.floor(nodes[k+1]-0.5))
                for x in range(xa,xb+1): self._set(x,y,c)

    def downsample(self):
        s=self.ss; W=self.W; out=bytearray(self.w*self.h*4)
        inv=1.0/(s*s)
        for y in range(self.h):
            for x in range(self.w):
                r=g=b=a=0
                for dy in range(s):
                    base=((y*s+dy)*W + x*s)*4
                    for dx in range(s):
                        i=base+dx*4
                        r+=self.buf[i]; g+=self.buf[i+1]; b+=self.buf[i+2]; a+=self.buf[i+3]
                o=(y*self.w+x)*4
                out[o]=int(r*inv); out[o+1]=int(g*inv); out[o+2]=int(b*inv); out[o+3]=int(a*inv)
        return out

    def save(self, path):
        rgba=self.downsample()
        def chunk(typ,data):
            return struct.pack(">I",len(data))+typ+data+struct.pack(">I",zlib.crc32(typ+data)&0xffffffff)
        ihdr=struct.pack(">IIBBBBB",self.w,self.h,8,6,0,0,0)
        raw=bytearray(); stride=self.w*4
        for y in range(self.h):
            raw.append(0); raw+=rgba[y*stride:(y+1)*stride]
        with open(path,'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n'); f.write(chunk(b'IHDR',ihdr))
            f.write(chunk(b'IDAT',zlib.compress(bytes(raw),9))); f.write(chunk(b'IEND',b''))

# ---------------- Colors ----------------
NAVY=(30,44,62)
GOLD=(244,167,44)
LIGHT=(245,249,255)
INK=(25,37,52)
TEAL=(70,98,124)

# ---------------- Stroke font (uppercase) ----------------
def arc(cx,cy,rx,ry,a0,a1,n=40):
    return [(cx+rx*math.cos(math.radians(a0+(a1-a0)*i/n)),
             cy+ry*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

GL={}
GL['I']=(.28,[[(.14,0),(.14,1)]])
GL['P']=(.60,[[(.08,0),(.08,1)],arc(.08,.26,.42,.26,-90,90)])
GL['D']=(.70,[[(.08,0),(.08,1)],arc(.08,.5,.58,.5,-90,90)])
GL['E']=(.56,[[(.08,.02),(.08,.98)],[(.08,.02),(.52,.02)],[(.08,.5),(.44,.5)],[(.08,.98),(.52,.98)]])
GL['T']=(.60,[[(.02,.02),(.58,.02)],[(.30,.02),(.30,1)]])
GL['C']=(.64,[arc(.34,.5,.30,.5,48,312,48)])
GL['G']=(.72,[arc(.36,.5,.32,.5,40,318,48),[(.68,.55),(.42,.55)],[(.68,.55),(.68,.28)]])
GL['V']=(.64,[[(.03,.02),(.32,.98),(.61,.02)]])
GL['S']=(.58,[[(.52,.16),(.40,.04),(.20,.03),(.08,.16),(.11,.31),(.28,.41),(.46,.51),(.52,.66),(.46,.85),(.28,.98),(.10,.93),(.04,.80)]])
GL['M']=(.82,[[(.07,.98),(.07,.02),(.41,.66),(.75,.02),(.75,.98)]])
GL['A']=(.72,[[(.04,.98),(.36,.02),(.68,.98)],[(.17,.64),(.55,.64)]])
GL['R']=(.66,[[(.08,0),(.08,1)],arc(.08,.27,.44,.27,-90,90),[(.30,.5),(.62,.98)]])
GL['K']=(.62,[[(.08,0),(.08,1)],[(.60,.02),(.12,.52)],[(.22,.44),(.62,.98)]])
GL['N']=(.68,[[(.08,.98),(.08,.02),(.62,.98),(.62,.02)]])
GL['L']=(.50,[[(.10,.02),(.10,.98),(.48,.98)]])
GL[' ']=(.34,[])
GL['.']=(.26,[[(.12,.92),(.15,.92)]])

def text_width(s,size,track):
    w=0
    for ch in s:
        adv,_=GL[ch]; w+=adv*size+track
    return w-track

def draw_text(c,s,x,y,size,sw,color,track=None):
    if track is None: track=0.10*size
    for ch in s:
        adv,strokes=GL[ch]
        for poly in strokes:
            pts=[(x+px*size,y+py*size) for px,py in poly]
            if len(pts)==1: continue
            c.polyline(pts,sw,color)
        x+=adv*size+track
    return x

# ---------------- Icon ----------------
def draw_icon(c,ox,oy,s):
    def P(x,y): return (ox+x*s, oy+y*s)
    # handle (behind lens)
    c.capsule(*P(300,304),*P(440,444),44*s,NAVY)
    # lens ring + glass
    cx,cy=300/ (1) ,0
    cx,cy=300,200
    c.fill_circle(ox+300*s, oy+200*s, 152*s, NAVY)
    c.fill_circle(ox+300*s, oy+200*s, 128*s, LIGHT)
    # chart dip (down then strong recovery)
    chart=[(214,176),(254,232),(300,286),(348,210),(404,132)]
    pts=[(ox+px*s,oy+py*s) for px,py in chart]
    c.polyline(pts,17*s,GOLD)
    # markers
    for px,py in chart:
        c.fill_circle(ox+px*s,oy+py*s,12*s,NAVY)
        c.fill_circle(ox+px*s,oy+py*s,6*s,LIGHT)
    # recovery up-arrow at end
    ex,ey=404,132
    tri=[(ex,ey-26),(ex-15,ey+6),(ex+15,ey+6)]
    c.fill_poly([(ox+a*s,oy+b*s) for a,b in tri],GOLD)

# ---------------- Build icon file (square, padded) ----------------
def build_icon():
    c=Canvas(512,512,ss=4)
    # offset so the magnifier (centered ~ (300,200) lens, handle to 440) fits 0..512
    draw_icon(c,-44,40,1.0)
    c.save('dipdetectives-icon.png')
    print('icon done')

# ---------------- Build horizontal logo ----------------
def build_logo():
    c=Canvas(1120,340,ss=3)
    # icon scaled on left
    scale=0.46
    draw_icon(c, -44*scale+24, 40*scale+44, scale)
    # wordmark
    tx=300; top=96; size=86; sw=12
    endx=draw_text(c,'DIP',tx,top,size,sw,GOLD)
    endx=draw_text(c,' ',endx,top,size,sw,GOLD)
    draw_text(c,'DETECTIVES',endx,top,size,sw,INK)
    # tagline
    draw_text(c,'MARKET DIP INTELLIGENCE',tx+4,228,24,3.2,TEAL,track=24*0.34)
    c.save('dipdetectives-logo.png')
    print('logo done')

if __name__=='__main__':
    build_icon()
    build_logo()
    print('all done')
