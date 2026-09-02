"""Gera os 36 efeitos WAV originais e o ícone do aplicativo."""
import math, random, struct, wave
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'assets'/'audio'; OUT.mkdir(parents=True,exist_ok=True)
RATE=44100
def tone(freq,t,dur=.75,kind=0):
    env=min(1,t/.025,max(0,(dur-t)/.12)); vibr=1+.018*math.sin(2*math.pi*5*t)
    if kind%5==0:return math.sin(2*math.pi*freq*vibr*t)*env
    if kind%5==1:return (1 if math.sin(2*math.pi*freq*t)>0 else -1)*env*.65
    if kind%5==2:return math.sin(2*math.pi*(freq+freq*1.8*t/dur)*t)*env
    if kind%5==3:return (math.sin(2*math.pi*freq*t)+.45*math.sin(2*math.pi*freq*1.5*t))*env*.65
    return math.sin(2*math.pi*freq*t)*math.sin(math.pi*t/dur)
random.seed(20260902)
for i in range(36):
    dur=.55+(i%6)*.11; freq=180+(i*73)%950; frames=[]
    for n in range(int(RATE*dur)):
        t=n/RATE; value=tone(freq,t,dur,i)
        if i in (8,20,21,32): value=value*.45+(random.random()*2-1)*.32*min(1,t/.03)*max(0,(dur-t)/.1)
        if i%7==0: value+=.28*tone(freq*1.5,t,dur,(i+2)%5)
        value=max(-1,min(1,value*.58)); sample=int(value*32767); frames.append(struct.pack('<hh',sample,sample))
    with wave.open(str(OUT/f'{i+1:02}.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(b''.join(frames))
img=Image.new('RGBA',(256,256),(12,13,15,255)); d=ImageDraw.Draw(img)
d.ellipse((44,44,212,212),outline=(255,138,0),width=18); d.ellipse((82,82,174,174),outline=(255,138,0),width=15); d.ellipse((111,111,145,145),fill=(255,138,0))
d.rectangle((118,20,138,70),fill=(12,13,15)); d.rectangle((118,186,138,236),fill=(12,13,15)); d.rectangle((20,118,70,138),fill=(12,13,15)); d.rectangle((186,118,236,138),fill=(12,13,15))
img.save(ROOT/'assets'/'icon.ico',sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])
