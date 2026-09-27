from pathlib import Path
import imageio.v3 as iio
import numpy as np
from PIL import Image,ImageEnhance,ImageOps,ImageDraw,ImageFont

IMG={".png",".jpg",".jpeg",".bmp",".webp"}
VID={".mp4",".avi",".mov",".mkv",".webm"}

def _video(p):
    out=[]
    for n,f in enumerate(iio.imiter(p,plugin="ffmpeg")):
        if n>=120: break
        a=np.asarray(f)
        if a.ndim==2:a=np.stack([a]*3,-1)
        if a.shape[-1]==4:a=a[...,:3]
        out.append(Image.fromarray(a.astype("uint8")).convert("RGB"))
    return out

def _effect(im,e):
    if e=="Grayscale": return ImageOps.grayscale(im).convert("RGB")
    if e=="Sepia": return Image.blend(ImageOps.grayscale(im).convert("RGB"),Image.new("RGB",im.size,(112,66,20)),.35)
    if e=="Brightness": return ImageEnhance.Brightness(im).enhance(1.25)
    if e=="Contrast": return ImageEnhance.Contrast(im).enhance(1.35)
    return im

def _text(im,text):
    if not text:return im
    d=ImageDraw.Draw(im); size=max(18,min(42,im.width//18))
    candidates=["C:/Windows/Fonts/arialbd.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    font=ImageFont.load_default()
    for p in candidates:
        if Path(p).exists():
            font=ImageFont.truetype(p,size);break
    box=d.textbbox((0,0),text,font=font); w=box[2]-box[0]; h=box[3]-box[1]
    x=max(8,(im.width-w)//2); y=max(8,im.height-h-24)
    d.rounded_rectangle((x-12,y-7,x+w+12,y+h+7),10,fill=(0,0,0,160)); d.text((x,y),text,font=font,fill="white")
    return im

def create_gif(paths,out,duration=150,loop=0,resize_width=None,effect="None",overlay_text=""):
    frames=[]
    for p in paths:
        p=Path(p)
        if p.suffix.lower() in IMG:
            with Image.open(p) as im: frames.append(im.convert("RGB"))
        elif p.suffix.lower() in VID: frames.extend(_video(p))
    if not frames: raise ValueError("No supported media found.")
    proc=[]
    for im in frames:
        if resize_width:
            h=max(1,round(im.height*resize_width/im.width)); im=im.resize((resize_width,h),Image.Resampling.LANCZOS)
        im=_effect(im,effect); im=_text(im.copy().convert("RGB"),overlay_text); proc.append(im)
    w=max(x.width for x in proc); h=max(x.height for x in proc)
    same=[]
    for im in proc:
        c=Image.new("RGB",(w,h),"black"); im.thumbnail((w,h),Image.Resampling.LANCZOS)
        c.paste(im,((w-im.width)//2,(h-im.height)//2)); same.append(c)
    out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    same[0].save(out,save_all=True,append_images=same[1:],duration=int(duration),loop=int(loop),optimize=True,disposal=2)
    return out
