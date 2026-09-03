from pathlib import Path
import numpy as np
import pygame

class Audio:
    def __init__(self,device=None):
        self.device=device; self.sound=None; self.samples=None; self.duration=0; self.paused=False; self.base_volume=0.8; self.gain=1.0
        self._init_mixer(device)
    def _init_mixer(self,device=None):
        pygame.mixer.pre_init(44100,-16,2,512)
        try: pygame.mixer.init(devicename=device)
        except Exception: pygame.mixer.init(); self.device=None
        self.channels=[pygame.mixer.Channel(0),pygame.mixer.Channel(1)]; self.active=0; self.channel=self.channels[0]
    def devices(self):
        try:
            from pygame._sdl2.audio import get_audio_device_names
            return ["Padrão do sistema"]+list(get_audio_device_names(False))
        except Exception:return ["Padrão do sistema"]
    def set_device(self,name):
        self.stop(); pygame.mixer.quit(); self.device=None if name=="Padrão do sistema" else name; self._init_mixer(self.device)
    def play(self,path:Path,volume):
        if self.sound:self.channel.fadeout(850)
        self.active=1-self.active; self.channel=self.channels[self.active]; self.sound=pygame.mixer.Sound(str(path)); self.duration=self.sound.get_length(); self.samples=pygame.sndarray.array(self.sound)
        mono=self.samples.mean(axis=1) if self.samples.ndim>1 else self.samples
        rms=float(np.sqrt(np.mean(mono.astype(np.float64)**2))) if mono.size else 0
        self.gain=min(1.8,7000/rms) if rms>1 else 1.0
        self.volume(volume); self.channel.play(self.sound,fade_ms=220)
    def fadeout(self,milliseconds=650):
        if self.sound:self.channel.fadeout(milliseconds)
    def stop(self):
        if hasattr(self,"channels"):
            for channel in self.channels:channel.stop()
        self.sound=None; self.samples=None; self.duration=0; self.paused=False
    def pause(self):
        if not self.sound:return False
        self.channel.unpause() if self.paused else self.channel.pause(); self.paused=not self.paused; return self.paused
    def volume(self,value):
        self.base_volume=value/100
        if hasattr(self,"channels"):
            for channel in self.channels:channel.set_volume(min(1.0,self.base_volume*self.gain))
    def spectrum(self,elapsed,bars=18):
        if self.samples is None:return [0.0]*bars
        rate=pygame.mixer.get_init()[0]; center=int(elapsed*rate); size=2048; start=max(0,center-size//2)
        chunk=self.samples[start:start+size]
        if chunk.size<128:return [0.0]*bars
        mono=chunk.mean(axis=1) if chunk.ndim>1 else chunk
        window=mono.astype(np.float64)*np.hanning(len(mono)); magnitudes=np.abs(np.fft.rfft(window))[1:]
        edges=np.geomspace(1,len(magnitudes),bars+1).astype(int); levels=[]
        for i in range(bars):
            band=magnitudes[edges[i]:max(edges[i]+1,edges[i+1])]
            levels.append(float(np.log1p(band.mean())))
        peak=max(levels) if levels else 1
        return [v/peak if peak else 0 for v in levels]
    def busy(self): return bool(self.channel.get_busy() or self.paused)
    def close(self): self.stop(); pygame.mixer.quit()
