#!/usr/bin/env python3
"""Candidate B: Giant celestial koi swimming through clouds over a lantern-lit village.
Bold single focal: vermillion/white/gold koi on deep indigo, swirling clouds,
dozens of floating glowing lanterns filling mid-ground, village foreground.
PIL+numpy, seeded, deterministic."""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

random.seed(202); np.random.seed(202)
W=H=1024; S=2; SW,SH=W*S,H*S

def catmull(points, samples=20, closed=False):
    pts=list(points)
    ext=([pts[-1]]+pts+[pts[0],pts[1]]) if closed else ([pts[0]]+pts+[pts[-1]])
    out=[]
    for i in range(len(ext)-3):
        p0,p1,p2,p3=ext[i],ext[i+1],ext[i+2],ext[i+3]
        for j in range(samples):
            t=j/samples; t2,t3=t*t,t*t*t
            out.append((0.5*((2*p1[0])+(-p0[0]+p2[0])*t+(2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2+(-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3),
                        0.5*((2*p1[1])+(-p0[1]+p2[1])*t+(2*p0[1]-5*p1[1]+4*p2[1]-p3[1])*t2+(-p0[1]+3*p1[1]-3*p2[1]+p3[1])*t3)))
    out.append(pts[-1] if not closed else pts[0])
    return out

# ---- sky ----
y=np.linspace(0,1,SH)[:,None]; x=np.linspace(0,1,SW)[None,:]
img=np.zeros((SH,SW,3),float)
top=np.array([12,8,44],float); mid=np.array([26,20,84],float); low=np.array([70,30,70],float)
for c in range(3):
    img[:,:,c]=np.where(y<0.62, top[c]+(mid[c]-top[c])*(y/0.62), mid[c]+(low[c]-mid[c])*((y-0.62)/0.38))
for (bx,by,br,col,st) in [(0.8,0.15,0.3,(150,50,140),0.5),(0.18,0.3,0.3,(30,110,160),0.5),(0.5,0.6,0.34,(200,90,40),0.28)]:
    d=np.sqrt((x-bx)**2+(y-by)**2); g=np.exp(-(d**2)/(2*(br*0.55)**2))*st
    for c in range(3): img[:,:,c]+=g*col[c]*0.55
small=np.array(Image.fromarray((np.random.rand(24,24)*255).astype(np.uint8)).resize((SW,SH),Image.BICUBIC),float)/255.0
img[:,:,0]+=(small-0.5)*20; img[:,:,1]+=(small-0.5)*14; img[:,:,2]+=(small-0.5)*28
img=Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert("RGBA")

# moon top-right small crescent glow
moon=Image.new("RGBA",(SW,SH),(0,0,0,0)); md=ImageDraw.Draw(moon)
mx,my,mr=872*S,128*S,62*S
for r,a in [(mr*2.4,13),(mr*1.6,26)]:
    md.ellipse([mx-r,my-r,mx+r,my+r],fill=(255,220,170,int(a)))
img=Image.alpha_composite(img,moon.filter(ImageFilter.GaussianBlur(15*S)))
m2=Image.new("RGBA",(SW,SH),(0,0,0,0)); m2d=ImageDraw.Draw(m2)
m2d.ellipse([mx-mr,my-mr,mx+mr,my+mr],fill=(255,238,205,255))
m2d.ellipse([mx-mr*0.55,my-mr*1.05,mx+mr*0.75,my+mr*0.35],fill=(30,22,80,255))
img=Image.alpha_composite(img,m2.filter(ImageFilter.GaussianBlur(1*S)))

# stars dense
stars=Image.new("RGBA",(SW,SH),(0,0,0,0)); sd=ImageDraw.Draw(stars)
for _ in range(1300):
    sx,sy=random.uniform(0,SW),random.uniform(0,SH*0.8)
    r=random.choice([1,1,1,2,2,3])*S//2; a=random.randint(50,255)
    col=random.choice([(215,238,255,a),(255,230,190,a),(255,205,215,a)])
    sd.ellipse([sx-r,sy-r,sx+r,sy+r],fill=col)
    if r>=3 and random.random()<0.4:
        L=r*5; sd.line([sx-L,sy,sx+L,sy],fill=(255,235,200,a//3),width=S); sd.line([sx,sy-L,sx,sy+L],fill=(255,235,200,a//3),width=S)
img=Image.alpha_composite(img,stars)

# aurora faint top (magenta/teal) for atmosphere
def ribbon(base_y,amp,col,alpha,thick,phase,blur):
    layer=Image.new("RGBA",(SW,SH),(0,0,0,0)); d=ImageDraw.Draw(layer)
    tops,bots=[],[]
    for xi in range(0,SW+16,16):
        t=xi/SW; yy=(base_y+amp*math.sin(t*3.4+phase)+26*math.sin(t*8+phase*2))*S
        tops.append((xi,yy)); bots.append((xi,yy+thick*S))
    d.polygon(tops+bots[::-1],fill=col+(alpha,))
    return layer.filter(ImageFilter.GaussianBlur(blur*S))
img=Image.alpha_composite(img,ribbon(40,40,(255,80,190),40,90,1.2,18))
img=Image.alpha_composite(img,ribbon(110,48,(50,230,200),48,110,3.6,14))

# ---- swirling clouds BEHIND koi ----
def cloud_layer(ylo,yhi,n,cols,alpha,blur,seed):
    lay=Image.new("RGBA",(SW,SH),(0,0,0,0)); d=ImageDraw.Draw(lay); rng=random.Random(seed)
    for i in range(n):
        cxp=rng.uniform(-60,1080)*S; cyp=rng.uniform(ylo,yhi)*S
        rx=rng.uniform(60,180)*S; ry=rx*rng.uniform(0.28,0.42)
        col=rng.choice(cols)
        d.ellipse([cxp-rx,cyp-ry,cxp+rx,cyp+ry],fill=col+(alpha,))
    return lay.filter(ImageFilter.GaussianBlur(blur*S))
img=Image.alpha_composite(img,cloud_layer(300,560,36,[(52,44,110),(66,54,130),(40,60,120)],200,8,21))
img=Image.alpha_composite(img,cloud_layer(280,480,26,[(150,140,200),(170,150,190)],60,12,22))

# ---- KOI: huge diagonal, head lower-left, tail upper-right curling ----
body_ctrl=[(88,600),(110,520),(190,450),(330,395),(500,362),(650,352),(770,360),
 (852,330),(918,262),(946,300),(920,378),(896,404),
 (916,470),(934,528),(896,500),(850,420),(828,398),
 (700,452),(540,492),(380,522),(240,548),(140,584),(96,606)]
body=[(a*S,b*S) for a,b in catmull(body_ctrl,samples=20,closed=True)]
mask=Image.new("L",(SW,SH),0); kd=ImageDraw.Draw(mask); kd.polygon(body,fill=255)
# pectoral fin (translucent, drawn later too) + tail already in body
fin=[(a*S,b*S) for a,b in catmull([(310,512),(345,522),(368,610),(350,676),(318,606),(298,530)],samples=16,closed=True)]
kd.polygon(fin,fill=255)
mask=mask.filter(ImageFilter.GaussianBlur(1.0*S))
# interior: koi patchwork — vermillion base, white patches, gold belly
wx=np.linspace(0,1,SW)[None,:]; wy=np.linspace(0,1,SH)[:,None]
inter=np.zeros((SH,SW,3),float)
verm=np.array([232,84,32],float); deepo=np.array([178,44,20],float); gold=np.array([250,178,60],float)
g=np.clip((1-wy)*1.4-0.25,0,1)
for c in range(3): inter[:,:,c]=deepo[c]+(verm[c]-deepo[c])*g
belly=np.exp(-(((wy-(0.50-0.04*wx))/0.07)**2))*0.0  # keep belly subtle via patches instead
# white/gold patches: guaranteed blotches (drawn clipped to mask below)
inter_img=Image.fromarray(np.clip(inter,0,255).astype(np.uint8)).convert("RGBA")
blot=Image.new("RGBA",(SW,SH),(0,0,0,0)); bd=ImageDraw.Draw(blot); rngb=random.Random(4)
patch_spots=[(0.16,0.47,90,(252,246,235)),(0.34,0.40,70,(252,246,235)),(0.52,0.46,84,(252,246,235)),(0.68,0.39,58,(255,214,120)),(0.80,0.44,66,(252,246,235)),(0.44,0.36,44,(255,214,120)),(0.24,0.40,46,(255,214,120)),(0.60,0.36,40,(252,246,235))]
for (fx,fy,fr,colp) in patch_spots:
    cxp,cyp=fx*SW,fy*SH
    for k in range(7):
        ox,oy=rngb.gauss(0,fr*0.35*S),rngb.gauss(0,fr*0.22*S); rr=rngb.uniform(0.4,0.85)*fr*S
        bd.ellipse([cxp+ox-rr,cyp+oy-rr*0.7,cxp+ox+rr,cyp+oy+rr*0.7],fill=colp+(235,))
blot=blot.filter(ImageFilter.GaussianBlur(3*S))
blot.putalpha(Image.composite(blot.split()[3],Image.new("L",(SW,SH),0),mask))
inter_img=Image.alpha_composite(inter_img,blot)
# scales: rows of arcs + speckles, clipped to mask
sc=Image.new("RGBA",(SW,SH),(0,0,0,0)); scd=ImageDraw.Draw(sc)
for row in range(16):
    for colidx in range(26):
        cxp=(90+colidx*36+ (18 if row%2 else 0))*S; cyp=(345+row*15)*S; rr=20*S
        scd.arc([cxp-rr,cyp-rr,cxp+rr,cyp+rr],start=20,end=160,fill=(120,30,10,90),width=2*S)
        scd.arc([cxp-rr,cyp-rr+3*S,cxp+rr,cyp+rr+3*S],start=20,end=160,fill=(255,220,180,60),width=1*S)
for _ in range(260):
    sx,sy=random.uniform(80*S,950*S),random.uniform(330*S,560*S); r=random.choice([1,2])
    scd.ellipse([sx-r,sy-r,sx+r,sy+r],fill=(60,20,10,random.randint(50,120)))
sc.putalpha(Image.composite(sc.split()[3],Image.new("L",(SW,SH),0),mask))
inter_img=Image.alpha_composite(inter_img,sc)
img.paste(inter_img,(0,0),mask)
# warm glow + rim (gold top)
glow=np.zeros((SH,SW,4),np.uint8)
ga=np.clip(np.array(mask.filter(ImageFilter.GaussianBlur(15*S)),float)*0.42,0,105)
glow[:,:,0]=255; glow[:,:,1]=150; glow[:,:,2]=70; glow[:,:,3]=ga.astype(np.uint8)
img=Image.alpha_composite(img,Image.fromarray(glow,"RGBA"))
rim=np.zeros((SH,SW,4),np.uint8); mf=np.array(mask,float)
down=np.array(mask.transform((SW,SH),Image.AFFINE,(1,0,0,0,1,-10*S)),float)
upper=np.clip(mf-down,0,255); edge=np.clip(np.array(mask.filter(ImageFilter.GaussianBlur(5*S)),float)-mf,0,255)
rim[:,:,0]=255; rim[:,:,1]=225; rim[:,:,2]=170; rim[:,:,3]=np.clip(upper*0.95+edge*0.55,0,255).astype(np.uint8)
img=Image.alpha_composite(img,Image.fromarray(rim,"RGBA").filter(ImageFilter.GaussianBlur(1.4*S)))
# translucent flowing fin overlay (front)
finlay=Image.new("RGBA",(SW,SH),(0,0,0,0)); fd=ImageDraw.Draw(finlay)
fd.polygon(fin,fill=(255,150,80,105))
for k in range(5):
    fd.line([(312*S+k*9*S,522*S),(330*S+k*7*S,640*S)],fill=(255,215,160,140),width=2*S)
img=Image.alpha_composite(img,finlay.filter(ImageFilter.GaussianBlur(1.5*S)))
# whiskers + eye
wl=Image.new("RGBA",(SW,SH),(0,0,0,0)); wld=ImageDraw.Draw(wl)
wld.line([(105*S,585*S),(58*S,612*S),(30*S,600*S)],fill=(255,240,220,220),width=3*S)
wld.line([(112*S,560*S),(66*S,540*S),(38*S,548*S)],fill=(255,240,220,200),width=3*S)
img=Image.alpha_composite(img,wl.filter(ImageFilter.GaussianBlur(0.8*S)))
eye=Image.new("RGBA",(SW,SH),(0,0,0,0)); ed=ImageDraw.Draw(eye); ex,ey=182*S,536*S
for r,a,col in [(30,60,(255,200,90)),(17,255,(255,224,150)),(10,255,(24,14,8)),(4,255,(255,255,255))]:
    ox=r//3 if col==(255,255,255) else 0; oy=-r//3 if col==(255,255,255) else 0
    ed.ellipse([ex+ox-r*S//2,ey+oy-r*S//2,ex+ox+r*S//2,ey+oy+r*S//2],fill=col+(a,))
img=Image.alpha_composite(img,eye)
# gold sparkle trail from tail
tr=Image.new("RGBA",(SW,SH),(0,0,0,0)); td=ImageDraw.Draw(tr)
for i in range(280):
    t=random.random(); px=(905+t*105+random.gauss(0,13))*S; py=(440-t*180+20*math.sin(t*7)+random.gauss(0,17*(0.4+t)))*S
    r=max(1.0,random.choice([1,2,2,3,4])*(1-t*0.5)); td.ellipse([px-r,py-r,px+r,py+r],fill=(255,205,110,int(205*(1-t)+30)))
img=Image.alpha_composite(img,tr.filter(ImageFilter.GaussianBlur(1.0*S)))

# ---- clouds IN FRONT (bottom of koi, dreamy, soft) ----
img=Image.alpha_composite(img,cloud_layer(575,690,24,[(70,60,130),(88,72,150)],120,10,31))
img=Image.alpha_composite(img,cloud_layer(545,640,16,[(190,175,220)],42,12,32))

# ---- floating lanterns: jittered grid so halos never tangle ----
lant=Image.new("RGBA",(SW,SH),(0,0,0,0)); ld=ImageDraw.Draw(lant)
rngl=random.Random(9)
lanterns=[]
for gx in range(6):
    for gy in range(4):
        if rngl.random()<0.22: continue
        lx=70+gx*172+rngl.uniform(-34,34); ly=618+gy*62+rngl.uniform(-14,14); lr=rngl.uniform(13,23)
        lanterns.append((lx,ly,lr))
lanterns.sort(key=lambda z:z[2])
for (lx,ly,lr) in lanterns:
    lxS,lyS,lrS=lx*S,ly*S,lr*S
    # halo (single soft ring, smaller)
    for rr,aa in [(lrS*1.8,40)]:
        ld.ellipse([lxS-rr,lyS-rr,lxS+rr,lyS+rr],fill=(255,170,80,aa))
    # body: warm gradient orb (drawn as stacked ellipses)
    ld.ellipse([lxS-lrS,lyS-lrS*1.2,lxS+lrS,lyS+lrS*1.2],fill=(255,150,60,255))
    ld.ellipse([lxS-lrS*0.7,lyS-lrS*0.9,lxS+lrS*0.7,lyS+lrS*0.9],fill=(255,196,105,255))
    ld.ellipse([lxS-lrS*0.35,lyS-lrS*0.55,lxS+lrS*0.35,lyS+lrS*0.55],fill=(255,232,170,255))
    ld.rectangle([lxS-lrS*0.5,lyS-lrS*1.32,lxS+lrS*0.5,lyS-lrS*1.12],fill=(150,60,30,255))
    ld.line([lxS,lyS+lrS*1.2,lxS,lyS+lrS*1.7],fill=(255,190,110,200),width=2*S)
img=Image.alpha_composite(img,lant.filter(ImageFilter.GaussianBlur(0.7*S)))
# lantern reflections sparkle band
sp=Image.new("RGBA",(SW,SH),(0,0,0,0)); spd=ImageDraw.Draw(sp)
for _ in range(500):
    sx=random.uniform(0,SW); sy=random.uniform(700*S,880*S); r=random.choice([1,1,2])*S//2
    spd.ellipse([sx-r,sy-r,sx+r,sy+r],fill=(255,190,110,random.randint(50,190)))
img=Image.alpha_composite(img,sp.filter(ImageFilter.GaussianBlur(0.7*S)))

# ---- village foreground: rooftops with tiled roofs + warm windows ----
vil=Image.new("RGBA",(SW,SH),(0,0,0,0)); vd=ImageDraw.Draw(vil)
rng=random.Random(12); base=SH; houses=[]
xx=-16
while xx<SW+30:
    bw=rng.randint(110,210)*S//2; bh=rng.randint(120,215)*S//2
    vd.rectangle([xx,base-bh,xx+bw,base],fill=(8,8,20,255))
    # tiled roof trapezoid
    vd.polygon([(xx-10*S,base-bh),(xx+bw+10*S,base-bh),(xx+bw-14*S,base-bh-30*S),(xx+14*S,base-bh-30*S)],fill=(24,16,44,255))
    vd.line([(xx-10*S,base-bh),(xx+bw+10*S,base-bh)],fill=(255,150,80,120),width=2*S)
    houses.append((xx,bw,bh)); xx+=bw+rng.randint(4,14)*S//2
for (hx,bw,bh) in houses:
    cols=max(1,bw//(20*S)); rows=max(1,bh//(22*S))
    for ci in range(cols):
        for ri in range(rows):
            if rng.random()<0.6:
                wxp=hx+10*S+ci*20*S; wyp=base-bh+12*S+ri*22*S
                vd.rectangle([wxp,wyp,wxp+10*S,wyp+12*S],fill=(255,196,100,rng.randint(170,255)))
                vd.line([wxp+5*S,wyp,wxp+5*S,wyp+12*S],fill=(8,8,20,200),width=1*S)
img=Image.alpha_composite(img,vil)

img=img.convert("RGB").resize((W,H),Image.LANCZOS)
arr=np.array(img).astype(float); arr+=np.random.normal(0,3.6,arr.shape[:2])[...,None]
yy2,xx2=np.mgrid[0:H,0:W]; dist=np.sqrt(((xx2-W/2)/(W*0.78))**2+((yy2-H/2)/(H*0.78))**2)
vig=np.clip(1-0.26*np.clip(dist-0.6,0,1)**2,0.74,1); arr*=vig[...,None]
img=Image.fromarray(np.clip(arr,0,255).astype(np.uint8)).filter(ImageFilter.UnsharpMask(radius=2,percent=85,threshold=2))
out=os.path.join(os.path.dirname(os.path.abspath(__file__)),"entry.png")
img.save(out,optimize=True)
if os.path.getsize(out)>1048576:
    img.quantize(colors=256,method=Image.Quantize.FASTOCTREE,dither=Image.Dither.FLOYDSTEINBERG).save(out,optimize=True)
print("saved",out,img.size,os.path.getsize(out))
