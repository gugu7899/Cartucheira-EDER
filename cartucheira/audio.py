from pathlib import Path
import pygame

class Audio:
    def __init__(self):
        pygame.mixer.pre_init(44100,-16,2,512); pygame.mixer.init()
        self.channel=pygame.mixer.Channel(0); self.sound=None; self.duration=0; self.paused=False
    def play(self,path:Path,volume):
        self.stop(); self.sound=pygame.mixer.Sound(str(path)); self.duration=self.sound.get_length()
        self.channel.set_volume(volume/100); self.channel.play(self.sound)
    def stop(self):
        self.channel.stop(); self.sound=None; self.duration=0; self.paused=False
    def pause(self):
        if not self.sound:return False
        self.channel.unpause() if self.paused else self.channel.pause(); self.paused=not self.paused; return self.paused
    def volume(self,value): self.channel.set_volume(value/100)
    def busy(self): return bool(self.channel.get_busy() or self.paused)
    def close(self): self.stop(); pygame.mixer.quit()
