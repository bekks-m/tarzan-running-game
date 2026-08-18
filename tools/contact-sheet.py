import sys,glob,re
from PIL import Image,ImageDraw
def tsec(f):
    m=re.search(r"t(\d+)_(\d+)",f); return int(m.group(1))+int(m.group(2))/1000
src,out=sys.argv[1],sys.argv[2]
step=int(sys.argv[3]) if len(sys.argv)>3 else 3
cols=int(sys.argv[4]) if len(sys.argv)>4 else 6
fs=sorted(glob.glob(src+"/*.png"),key=tsec)[::step]
tw,th=300,198
rows=(len(fs)+cols-1)//cols
sheet=Image.new("RGB",(cols*tw,rows*(th+16)),(20,20,20))
d=ImageDraw.Draw(sheet)
for i,f in enumerate(fs):
    im=Image.open(f).convert("RGB").resize((tw,th))
    x,y=(i%cols)*tw,(i//cols)*(th+16)
    sheet.paste(im,(x,y+16))
    d.text((x+4,y+3),f"{tsec(f):.3f}",fill=(255,255,0))
sheet.save(out)
print(f"{len(fs)} frames -> {out}  ({sheet.size[0]}x{sheet.size[1]})")
