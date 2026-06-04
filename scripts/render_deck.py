#!/usr/bin/env python3
"""Render the Ladnut Storefront Visual Layout deck to PDF and PNG previews with libcairo."""
from __future__ import annotations
import ctypes, math, os, textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_OUT = ROOT / "Ladnut Storefront Visual Layout.pdf"
PREVIEWS = ROOT / "previews"
SVG_PREVIEWS = ROOT / "previews-svg"
W, H = 1600, 1200
NAVY=(0x26/255,0x38/255,0x4A/255); GREEN=(0x5E/255,0x94/255,0x7D/255); CREAM=(0xF7/255,0xF3/255,0xEA/255)
WHITE=(1,1,1); MIST=(0xDD/255,0xE8/255,0xEE/255); SAGE=(0xA8/255,0xB8/255,0xA1/255); TAUPE=(0xC6/255,0xB5/255,0xA3/255)
INK=(0x40/255,0x50/255,0x5F/255); MUTED=(0x66/255,0x75/255,0x82/255); ROSE=(0xF3/255,0xE8/255,0xE3/255); RED=(0xB5/255,0x6B/255,0x62/255)

cairo=ctypes.CDLL("libcairo.so.2")
class Ext(ctypes.Structure):
    _fields_=[('xb',ctypes.c_double),('yb',ctypes.c_double),('w',ctypes.c_double),('h',ctypes.c_double),('xa',ctypes.c_double),('ya',ctypes.c_double)]
for name,args in {
 'cairo_pdf_surface_create':[ctypes.c_char_p,ctypes.c_double,ctypes.c_double], 'cairo_svg_surface_create':[ctypes.c_char_p,ctypes.c_double,ctypes.c_double], 'cairo_image_surface_create':[ctypes.c_int,ctypes.c_int,ctypes.c_int],
 'cairo_create':[ctypes.c_void_p], 'cairo_destroy':[ctypes.c_void_p], 'cairo_surface_destroy':[ctypes.c_void_p], 'cairo_surface_write_to_png':[ctypes.c_void_p,ctypes.c_char_p],
 'cairo_set_source_rgb':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double], 'cairo_set_source_rgba':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double],
 'cairo_rectangle':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double], 'cairo_fill':[ctypes.c_void_p], 'cairo_stroke':[ctypes.c_void_p],
 'cairo_move_to':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double], 'cairo_line_to':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double], 'cairo_curve_to':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double],
 'cairo_arc':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double,ctypes.c_double], 'cairo_new_sub_path':[ctypes.c_void_p], 'cairo_close_path':[ctypes.c_void_p],
 'cairo_set_line_width':[ctypes.c_void_p,ctypes.c_double], 'cairo_select_font_face':[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_int,ctypes.c_int], 'cairo_set_font_size':[ctypes.c_void_p,ctypes.c_double],
 'cairo_show_text':[ctypes.c_void_p,ctypes.c_char_p], 'cairo_text_extents':[ctypes.c_void_p,ctypes.c_char_p,ctypes.POINTER(Ext)], 'cairo_show_page':[ctypes.c_void_p],
 'cairo_save':[ctypes.c_void_p], 'cairo_restore':[ctypes.c_void_p], 'cairo_clip':[ctypes.c_void_p], 'cairo_translate':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double], 'cairo_scale':[ctypes.c_void_p,ctypes.c_double,ctypes.c_double], 'cairo_rotate':[ctypes.c_void_p,ctypes.c_double]
}.items():
    getattr(cairo,name).argtypes=args
for name in ['cairo_pdf_surface_create','cairo_svg_surface_create','cairo_image_surface_create','cairo_create']:
    getattr(cairo,name).restype=ctypes.c_void_p
CAIRO_FORMAT_ARGB32=0; NORMAL=0; BOLD=1

def rgb(ctx,col,a=1):
    if a==1: cairo.cairo_set_source_rgb(ctx,*col)
    else: cairo.cairo_set_source_rgba(ctx,*col,a)
def rr(ctx,x,y,w,h,r):
    cairo.cairo_new_sub_path(ctx); cairo.cairo_arc(ctx,x+w-r,y+r,r,-math.pi/2,0); cairo.cairo_arc(ctx,x+w-r,y+h-r,r,0,math.pi/2); cairo.cairo_arc(ctx,x+r,y+h-r,r,math.pi/2,math.pi); cairo.cairo_arc(ctx,x+r,y+r,r,math.pi,3*math.pi/2); cairo.cairo_close_path(ctx)
def fill_rr(ctx,x,y,w,h,r,col,a=1): rgb(ctx,col,a); rr(ctx,x,y,w,h,r); cairo.cairo_fill(ctx)
def stroke_rr(ctx,x,y,w,h,r,col,lw=2,a=1): rgb(ctx,col,a); cairo.cairo_set_line_width(ctx,lw); rr(ctx,x,y,w,h,r); cairo.cairo_stroke(ctx)
def circle(ctx,x,y,r,col,a=1): rgb(ctx,col,a); cairo.cairo_arc(ctx,x,y,r,0,math.tau); cairo.cairo_fill(ctx)
def line(ctx,x1,y1,x2,y2,col,lw=4,a=1): rgb(ctx,col,a); cairo.cairo_set_line_width(ctx,lw); cairo.cairo_move_to(ctx,x1,y1); cairo.cairo_line_to(ctx,x2,y2); cairo.cairo_stroke(ctx)
def font(ctx,size,bold=False): cairo.cairo_select_font_face(ctx,b"DejaVu Sans",0,BOLD if bold else NORMAL); cairo.cairo_set_font_size(ctx,size)
def width(ctx,s,size,bold=False): font(ctx,size,bold); e=Ext(); cairo.cairo_text_extents(ctx,s.encode(),ctypes.byref(e)); return e.xa
def text(ctx,s,x,y,size=24,col=INK,bold=False,center=False,maxw=None,lh=1.35):
    # Allow compact calls like text(..., False, 520) to mean max width.
    if isinstance(center, (int, float)) and center not in (0, 1) and maxw is None:
        maxw = center
        center = False
    font(ctx,size,bold); rgb(ctx,col)
    if maxw:
        words=s.split(); lines=[]; cur=""
        for wd in words:
            t=(cur+" "+wd).strip()
            if width(ctx,t,size,bold)<=maxw or not cur: cur=t
            else: lines.append(cur); cur=wd
        if cur: lines.append(cur)
        for i,l in enumerate(lines): text(ctx,l,x,y+i*size*lh,size,col,bold,center)
        return y+len(lines)*size*lh
    if center: x-=width(ctx,s,size,bold)/2
    cairo.cairo_move_to(ctx,x,y); cairo.cairo_show_text(ctx,s.encode('utf-8'))
    return y+size*lh
def title(ctx,s,x=140,y=130,size=62):
    fill_rr(ctx,x-48,y-58,8,86,4,GREEN); text(ctx,s,x,y,size,NAVY,True)
def footer(ctx): text(ctx,"Ladnut",1450,1140,19,(0.7,0.73,0.76),True,center=True)
def bg(ctx,col=WHITE): rgb(ctx,col); cairo.cairo_rectangle(ctx,0,0,W,H); cairo.cairo_fill(ctx)
def shadow_card(ctx,x,y,w,h,r=28,fill=WHITE): fill_rr(ctx,x+12,y+16,w,h,r,(0,0,0),.045); fill_rr(ctx,x,y,w,h,r,fill); stroke_rr(ctx,x,y,w,h,r,NAVY,1,.08)
def pill(ctx,s,x,y,col=GREEN): fill_rr(ctx,x,y,width(ctx,s,17,True)+30,34,17,(0.93,0.96,0.94)); text(ctx,s,x+15,y+23,17,col,True)

def dog(ctx,x,y,sc=1):
    cairo.cairo_save(ctx); cairo.cairo_translate(ctx,x,y); cairo.cairo_scale(ctx,sc,sc); fill_rr(ctx,30,80,230,120,55,(0.84,0.63,0.39)); circle(ctx,65,45,48,(0.84,0.63,0.39)); circle(ctx,98,53,18,(0.48,0.35,0.24)); line(ctx,250,105,310,70,(0.84,0.63,0.39),18); circle(ctx,55,42,7,NAVY); fill_rr(ctx,60,190,28,70,12,(0.84,0.63,0.39)); fill_rr(ctx,190,190,28,70,12,(0.84,0.63,0.39)); cairo.cairo_restore(ctx)
def cat(ctx,x,y,sc=1):
    cairo.cairo_save(ctx); cairo.cairo_translate(ctx,x,y); cairo.cairo_scale(ctx,sc,sc); fill_rr(ctx,30,90,150,95,45,(0.55,0.48,0.39)); circle(ctx,55,70,42,(0.55,0.48,0.39)); line(ctx,170,125,235,155,(0.55,0.48,0.39),13); circle(ctx,48,68,6,NAVY); cairo.cairo_restore(ctx)
def device(ctx,x,y,sc=1):
    cairo.cairo_save(ctx); cairo.cairo_translate(ctx,x,y); cairo.cairo_scale(ctx,sc,sc); fill_rr(ctx,0,0,140,180,34,(0.98,0.99,0.98)); stroke_rr(ctx,0,0,140,180,34,NAVY,2,.12); circle(ctx,70,58,32,MIST); circle(ctx,70,58,15,GREEN); fill_rr(ctx,38,120,64,18,9,(0.86,0.9,0.9)); text(ctx,"PRODUCT",70,154,12,MUTED,True,True); cairo.cairo_restore(ctx)
def jar(ctx,x,y,sc=1):
    cairo.cairo_save(ctx); cairo.cairo_translate(ctx,x,y); cairo.cairo_scale(ctx,sc,sc); fill_rr(ctx,0,0,150,190,18,WHITE); stroke_rr(ctx,0,0,150,190,18,NAVY,2,.10); fill_rr(ctx,0,54,150,86,0,GREEN); text(ctx,"Daily",75,90,19,WHITE,True,True); text(ctx,"Wellness",75,116,16,WHITE,True,True); fill_rr(ctx,18,-18,114,28,10,(0.92,0.92,0.90)); cairo.cairo_restore(ctx)
def chew(ctx,x,y,sc=1):
    cairo.cairo_save(ctx); cairo.cairo_translate(ctx,x,y); cairo.cairo_scale(ctx,sc,sc); fill_rr(ctx,0,0,170,140,24,(0.93,0.80,0.58)); stroke_rr(ctx,0,0,170,140,24,NAVY,2,.08); [circle(ctx,a,b,16,(0.52,0.40,0.25)) for a,b in [(45,45),(105,70),(75,105)]]; cairo.cairo_restore(ctx)
def lifestyle(ctx,x,y,w,h,kind='home'):
    fill_rr(ctx,x,y,w,h,28,(0.94,0.90,0.80)); fill_rr(ctx,x+w*.58,y+60,w*.28,h*.28,20,(0.88,0.94,0.96)); fill_rr(ctx,x+w*.05,y+h*.72,w*.75,h*.16,45,TAUPE); dog(ctx,x+w*.58,y+h*.63,.75); cat(ctx,x+w*.25,y+h*.67,.65); fill_rr(ctx,x+w*.15,y+h*.38,75,210,32,GREEN); circle(ctx,x+w*.19,y+h*.31,38,(0.78,0.55,0.43))

def render_slide(ctx,n):
    bg(ctx, CREAM if n in [4,7,8,10,14] else WHITE)
    if n==1:
        text(ctx,"Storefront",640,520,82,NAVY,True,True); text(ctx,"Visual Layout",1010,520,82,GREEN,True,True)
        text(ctx,"A strategic high-conversion Amazon Storefront visual framework for Ladnut, integrating OzoIon CleanAir System™ and CareRhythm™ Daily Wellness for the North American pet market.",800,610,27,INK,False,True,980)
        text(ctx,"Ladnut | Amazon Storefront Planning Deck",800,1045,23,MUTED,True,True); circle(ctx,1320,170,70,GREEN,.10); return
    if n==2:
        fill_rr(ctx,0,0,W,H,0,(0.86,0.91,0.90)); fill_rr(ctx,870,160,450,300,26,(1,1,1),.55); fill_rr(ctx,850,770,470,130,50,TAUPE); dog(ctx,1140,720,1.0); cat(ctx,900,725,.75)
        fill_rr(ctx,90,150,650,760,36,WHITE,.85); text(ctx,"Brand Hero / Home Page First Screen",150,225,17,GREEN,True); text(ctx,"Cleaner Homes.",150,340,68,NAVY,True); text(ctx,"Healthier Routines.",150,425,68,NAVY,True); text(ctx,"Happier Pets.",150,510,68,NAVY,True)
        text(ctx,"Smart air care and daily wellness solutions designed to help pet families create cleaner spaces, easier routines, and more comfortable lives.",150,590,25,INK,False,520); fill_rr(ctx,150,735,190,58,28,GREEN); text(ctx,"Explore Clean Air",245,772,18,WHITE,True,True); fill_rr(ctx,365,735,210,58,28,NAVY); text(ctx,"Shop Daily Wellness",470,772,18,WHITE,True,True); return
    if n==3:
        title(ctx,"The Home We Share"); text(ctx,"Better care should feel easier for people and kinder for pets.",140,300,40,NAVY,True,600)
        text(ctx,"Pet life brings love, but it also brings odors, brushing battles, aging worries, and daily care routines that can be hard to keep up with. Ladnut was created to make everyday pet care cleaner, smarter, and easier to repeat — from litter box odor control to oral care and senior dog wellness.",140,420,25,INK,False,650)
        text(ctx,"Cleaner spaces. Easier routines. More comfortable pets.",140,760,32,GREEN,True); shadow_card(ctx,940,235,510,610,34); lifestyle(ctx,964,259,462,562); return
    if n==4:
        title(ctx,"Two Systems, One Shared Home"); cards=[("Clean Air & Odor Control","Powered by the OzoIon CleanAir System™, our clean air series uses ozone to help break down odor-causing molecules and negative ions to help purify lingering airborne residues in pet spaces.","Ozone + Negative Ion Air Care"),("Daily Wellness Care","Powered by CareRhythm™ Daily Wellness, our pet care series helps families build easier daily routines for oral hygiene, senior support, and everyday vitality.","Simple Daily Pet Wellness"),("Future Pet Home Care","A scalable brand system built to grow into pet-room air care, dander support, oral care, senior wellness, digestion, calming, and mobility routines.","Built to Grow")]
        for i,(h,body,tag) in enumerate(cards):
            x=95+i*500; shadow_card(ctx,x,230,455,760,30); fill_rr(ctx,x+25,255,405,300,20,MIST if i!=1 else (0.96,0.91,0.82));
            (device(ctx,x+205,330,1.2), cat(ctx,x+65,435,.55)) if i==0 else ((jar(ctx,x+105,315,.85), chew(ctx,x+245,340,.7), dog(ctx,x+300,430,.45)) if i==1 else (device(ctx,x+210,305,1.35), line(ctx,x+110,415,x+340,375,GREEN,5,.35)))
            text(ctx,h,x+38,630,31,NAVY,True,maxw=370); text(ctx,body,x+38,700,20,INK,False,365); pill(ctx,tag,x+38,925)
        return
    if n==5:
        bg(ctx,(0.96,0.985,0.995)); title(ctx,"OzoIon CleanAir System™"); text(ctx,"Ozone odor breakdown + negative ion residue purification",140,175,27,GREEN,True)
        text(ctx,"Pet odors are not just smells. They often come from odor-causing molecules, airborne residues, dust, and pet dander released by litter, moisture, urine, and daily pet activity. OzoIon CleanAir System™ is designed to help care for pet air in two ways: ozone helps break down odor molecules, while negative ions help attract lingering airborne particles and residues.",95,285,23,INK,False,670)
        for j,(ic,h,b) in enumerate([("O3","Ozone Odor Breakdown","Helps break down odor-causing molecules commonly associated with litter box use and daily pet activity."),("−","Negative Ion Residue Purification","Helps attract airborne particles such as dust, pet dander, and lingering odor residues."),("≈","Freshness Without Heavy Fragrance","Supports a cleaner-feeling space without relying on overpowering perfume sprays.")]):
            y=560+j*135; fill_rr(ctx,95,y,58,58,16,(0.92,0.96,0.94)); text(ctx,ic,124,y+38,21,GREEN,True,True); text(ctx,h,175,y+25,24,NAVY,True); text(ctx,b,175,y+60,19,INK,False,570)
        shadow_card(ctx,825,250,610,680,32,(0.98,1,1)); labels=[("Odor molecules\ndust + dander",930),("O3 + negative ions",1125),("Cleaner-feeling air\nfresh pet space",1325)]
        for txt,x in labels: fill_rr(ctx,x-88,435,176,250,28,WHITE); text(ctx,txt,x,535,24,NAVY,True,True,150); 
        for x in [1018,1215]: text(ctx,"→",x,560,60,GREEN,True,True)
        for x,y in [(900,395),(970,470),(910,620),(1160,470),(1110,625),(1310,445),(1370,590)]: circle(ctx,x,y,18,GREEN if x>1050 else TAUPE,.45)
        return
    if n==6:
        bg(ctx,(0.96,0.985,0.995)); title(ctx,"Clean Air, Built for Pet Homes"); y=205
        secs=[("Hero Banner","Clean air, built for pet homes. OzoIon CleanAir System™ uses ozone to help break down odor-causing molecules and negative ions to help purify lingering airborne residues — supporting fresher, cleaner pet spaces."),("Problem Definition","Pet odor is more than a smell problem. It is an air-quality problem."),("OzoIon Technical Principle","Ozone + negative ions in a simple source-focused air care story."),("Product Feature Block","Dual-action freshness for litter box spaces."),("Usage Scenarios","Apartment Living   Laundry Rooms   Bathrooms   Multi-Cat Homes"),("Future Expansion","Pet room air care, purifier concepts, and dander-support routines.")]
        for i,(h,b) in enumerate(secs): shadow_card(ctx,180,y,1240,120 if i!=0 else 160,22,(0.98,1,1)); pill(ctx,h,210,y+22); text(ctx,b,210,y+76,22,NAVY if i in [0,1,3] else INK,True if i in [0,1,3] else False, maxw=900); device(ctx,1255,y+30,.5) if i in [0,3] else None; y += (150 if i!=0 else 190)
        return
    if n==7:
        title(ctx,"CareRhythm™ Daily Wellness"); fill_rr(ctx,110,235,590,690,290,(0.92,0.88,0.78)); dog(ctx,310,580,1.1); jar(ctx,190,350,.75); chew(ctx,480,410,.65)
        text(ctx,"Small routines can protect the bigger life you share.",805,300,48,NAVY,True,560); text(ctx,"The best pet care is not always the most complicated. It is the care your pet will accept and your family can repeat. CareRhythm™ Daily Wellness is Ladnut’s approach to daily care — simple, science-informed products designed to fit into real feeding, aging, and wellness routines.",805,430,24,INK,False,560)
        for i,(h,items) in enumerate([("Oral Care Routine",["Mealtime powder","Fresher breath support","No brushing battle","Daily repeatability"]),("Senior Wellness Routine",["Daily soft chew","Immune balance support","Easy senior care","Long-term care mindset"])]):
            x=805+i*300; shadow_card(ctx,x,745,270,250,24); text(ctx,h,x+25,790,23,NAVY,True); yy=830
            for it in items: text(ctx,"• "+it,x+25,yy,18,INK); yy+=31
        return
    if n==8:
        title(ctx,"Daily care, made easier to keep."); shadow_card(ctx,125,205,1350,135,24); pill(ctx,"Hero + CareRhythm Philosophy",155,232); text(ctx,"Simple daily care that fits real feeding, aging, and wellness routines.",155,300,28,NAVY,True)
        rows=[("Ladnut Dog Dental Powder","No-fight oral care for everyday freshness.",["Easy mealtime dental routine","Helps support fresher breath","Designed for dogs who resist brushing","Sprinkle over food and serve"],jar), ("Ladnut Mushroom Chews for Dogs","Inside-out support for aging dogs.",["Functional mushroom blend","Daily senior wellness support","Helps support immune balance","Supports normal cellular wellness"],chew)]
        y=400
        for h,sub,items,draw in rows:
            shadow_card(ctx,145,y,600,315,26); fill_rr(ctx,175,y+45,200,220,22,(0.98,0.95,0.88)); draw(ctx,215,y+78,.75); text(ctx,h,400,y+75,29,NAVY,True,maxw=300); text(ctx,sub,400,y+120,20,GREEN,True,maxw=310); yy=y+160
            for it in items: text(ctx,"• "+it,400,yy,18,INK); yy+=31
            y+=355
        shadow_card(ctx,820,430,430,280,26); pill(ctx,"Shared System Logic",850,465); text(ctx,"Oral care, senior wellness, digestion, calming, and mobility routines can share one repeatable brand architecture.",850,545,25,NAVY,True,350)
        shadow_card(ctx,820,780,430,180,26); pill(ctx,"Future CareRhythm Expansion",850,820); text(ctx,"Built for easy future subpage expansion.",850,890,25,NAVY,True,330); return
    if n==9:
        title(ctx,"Our Fresh Start Promise"); text(ctx,"Care should reach beyond the homes that buy our products.",140,185,27,GREEN,True); text(ctx,"Through the Ladnut Fresh Start Program, our long-term goal is to support cleaner, calmer spaces for shelter pets, foster homes, and rescue families. We believe every pet deserves a healthier place to wait, heal, and be loved.",140,265,25,INK,False,1100)
        for i,(ic,h,b) in enumerate([("⌂","Shelter Air Support","We aim to support rescue and foster environments with air care education and product-based support where it can make daily care easier."),("≈","Low-Fragrance Pet Home Education","We encourage pet families to reduce reliance on heavy fragrance sprays and move toward source-focused, routine-based air care."),("♥","Senior Pet Wellness Awareness","We believe senior pets deserve daily routines that support comfort, dignity, and long-term companionship.")]):
            x=105+i*500; shadow_card(ctx,x,520,455,420,28); fill_rr(ctx,x,520,455,9,0,GREEN); fill_rr(ctx,x+38,575,58,58,16,(0.92,0.96,0.94)); text(ctx,ic,x+67,614,28,GREEN,True,True); text(ctx,h,x+38,690,29,NAVY,True,maxw=350); text(ctx,b,x+38,780,22,INK,False,365)
        return
    if n==10:
        title(ctx,"Born for the real homes pets live in."); y=230
        for h,b in [("About Hero","Warm pet-family imagery sets the tone for the Ladnut story."),("Our Story","Built around cleaner air, easier routines, and happier everyday lives for pets and the people who love them."),("Ladnut Fresh Start Program","Positive foster and shelter support storytelling without sadness-led or unsupported donation claims.")]: shadow_card(ctx,100,y,780,150,22); pill(ctx,h,130,y+25); text(ctx,b,130,y+88,24,NAVY,True,680); y+=180
        shadow_card(ctx,100,770,780,180,22); text(ctx,"Mission Pillars",130,820,27,NAVY,True); [fill_rr(ctx,130+(i%2)*330,850+(i//2)*55,300,40,20,(0.92,0.96,0.94)) or text(ctx,t,280+(i%2)*330,877+(i//2)*55,17,GREEN,True,True) for i,t in enumerate(["Cleaner Shared Spaces","Easier Daily Routines","Science with Warmth","Kindness Beyond the Product"])]
        shadow_card(ctx,950,250,410,430,30); lifestyle(ctx,972,272,366,386); shadow_card(ctx,950,735,410,180,24); text(ctx,"Responsibility & Sustainability",980,785,25,NAVY,True,maxw=330); [pill(ctx,t,980,820+i*42) for i,t in enumerate(["Rechargeable product design","Less heavy fragrance","Routine-based care"])] ; return
    if n==11:
        title(ctx,"Assets Needed to Build"); cols=[("Must-Have Assets",["Ladnut logo","Cat litter box deodorizer 3D render","Cat deodorizer internal structure render","Dog dental powder product image","Mushroom chews product image"]),("AI / Design-Generated Assets",["Home pet family lifestyle image","Litter box clean-air lifestyle scene","OzoIon technology diagram","Negative ion particle-settling diagram","Dog mealtime care scene","Senior dog companionship scene","Shelter / foster home positive image"])]
        for i,(h,items) in enumerate(cols): x=125+i*720; shadow_card(ctx,x,250,650,510,28); text(ctx,h,x+50,330,32,NAVY,True); yy=390
        # redraw lists separately
        for i,(h,items) in enumerate(cols):
            x=125+i*720; yy=390
            for it in items: text(ctx,"✓  "+it,x+55,yy,24,INK); yy+=55
        shadow_card(ctx,125,825,1370,160,28,NAVY); text(ctx,"Amazon Specs Reminder",170,885,30,WHITE,True); [fill_rr(ctx,170+i*320,915,290,42,21,(1,1,1),.16) or text(ctx,t,315+i*320,943,14,WHITE,True,True) for i,t in enumerate(["Hero: 3000 × 600 px min","Logo: 400 × 400 px min","Keep text in safe area","Avoid crowded image text"])] ; return
    if n==12:
        title(ctx,"Compliance Guardrails"); lists=[("Recommended Language",GREEN,["helps break down odor molecules","helps address odor at the source","helps purify lingering airborne residues","supports a fresher environment","negative ion support","designed for litter box odor zones","pet-aware sensing","use as directed","helps support daily oral hygiene","helps support immune balance","supports normal cellular wellness","daily wellness routine"]),("Avoid",RED,["eliminates all odor","kills 99.9% of bacteria","completely safe ozone","100% non-toxic in all use conditions","sterilizes the air","medical-grade purification","prevents disease","treats dental disease","cures bad breath","shrinks lumps","anti-cancer","tumor support","best / #1 / most effective"])]
        for i,(h,col,items) in enumerate(lists): x=115+i*735; shadow_card(ctx,x,230,650,740,26,WHITE if i==0 else (1,.975,.965)); fill_rr(ctx,x,230,650,10,0,col); text(ctx,h,x+45,300,31,col,True); yy=355
        for i,(h,col,items) in enumerate(lists):
            x=115+i*735; yy=355
            for it in items: text(ctx,"• "+it,x+50,yy,20,INK); yy+=43
        fill_rr(ctx,115,1010,1370,75,20,(1,.96,.90)); text(ctx,"Ozone-related claims should remain controlled and support-oriented. Use “helps break down odor molecules” and “use as directed,” not absolute safety or sterilization claims.",145,1058,21,INK,False,maxw=1290); return
    if n==13:
        text(ctx,"Ready to Build?",800,510,96,GREEN,True,True); text(ctx,"This visual framework is ready to guide Ladnut’s Amazon Storefront design, asset creation, and internal approval discussion.",800,610,27,INK,False,True,900); text(ctx,"Next step: confirm final assets, review trademark usage, and create high-fidelity page mockups for Home, Clean Air, Daily Wellness, and Our Impact.",800,965,20,MUTED,False,True,1000); return
    if n==14:
        title(ctx,"Image Sources & Asset Notes"); y=250; rows=[("Design-generated placeholder lifestyle imagery","AI-generated placeholder lifestyle image for internal layout discussion only. Final Amazon Storefront images should be refined and replaced with brand-approved assets before publishing."),("CSS/SVG product placeholder blocks","Cat deodorizer, dog dental powder, mushroom chews, and future air care forms are intentionally schematic placeholders and should not be treated as final product appearance."),("OzoIon technology diagram","Created as an editable infographic to explain odor molecules, O3, negative ions, and cleaner-feeling air without sterilization or absolute safety claims."),("Amazon Storefront module thumbnails","Editable visual-layout approximations for Hero, Image with Text, Product Grid, Shoppable Image, Text Tile, and Video/Image Tile planning."),("Brand-approved assets still needed","Replace all placeholders with final Ladnut logo, approved product renders, packaging photography, internal structure render, and approved lifestyle photography before publication."),("No external stock imagery used","This deck uses locally authored editable visuals only; there are no third-party image licenses embedded in the PDF.")]
        text(ctx,"Thumbnail",145,215,17,GREEN,True); text(ctx,"Source / Asset Type",310,215,17,GREEN,True); text(ctx,"Usage Note",690,215,17,GREEN,True)
        for h,b in rows: shadow_card(ctx,105,y,1390,105,18); fill_rr(ctx,135,y+24,86,56,12,MIST); circle(ctx,195,y+61,15,TAUPE); text(ctx,h,300,y+45,21,NAVY,True,maxw=340); text(ctx,b,690,y+35,17,INK,False,maxw=740); y+=124
        return

def render_surface(surface):
    ctx=cairo.cairo_create(surface)
    for n in range(1,15): render_slide(ctx,n); footer(ctx); cairo.cairo_show_page(ctx)
    cairo.cairo_destroy(ctx)

def main():
    PREVIEWS.mkdir(exist_ok=True)
    SVG_PREVIEWS.mkdir(exist_ok=True)
    surf=cairo.cairo_pdf_surface_create(str(PDF_OUT).encode(), W, H); render_surface(surf); cairo.cairo_surface_destroy(surf)
    for n in range(1,15):
        surf=cairo.cairo_image_surface_create(CAIRO_FORMAT_ARGB32, W, H); ctx=cairo.cairo_create(surf); render_slide(ctx,n); footer(ctx); cairo.cairo_destroy(ctx); cairo.cairo_surface_write_to_png(surf, str(PREVIEWS/f"page-{n:02d}.png").encode()); cairo.cairo_surface_destroy(surf)
        surf=cairo.cairo_svg_surface_create(str(SVG_PREVIEWS/f"page-{n:02d}.svg").encode(), W, H); ctx=cairo.cairo_create(surf); render_slide(ctx,n); footer(ctx); cairo.cairo_show_page(ctx); cairo.cairo_destroy(ctx); cairo.cairo_surface_destroy(surf)
    print(f"Rendered 14 slides: {PDF_OUT.name}, previews/page-01.png … page-14.png, and previews-svg/page-01.svg … page-14.svg")
if __name__=="__main__": main()
