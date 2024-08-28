import bge
import aud
from collections import OrderedDict

class sound(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        self.device = aud.Device()
        self.handle = 0
        self.volume = 1.5
        self.cam = self.object.scene.objects['Camera']

    def update(self):
        pass
    
    def load(self, sound, delay=0):
        path = bge.logic.expandPath(f"//assets/sounds/SFX/{sound}.ogg")
        sound = aud.Sound(path)
        sound = sound.delay(delay)
        return aud.Sound.cache(sound)
    
    def play(self, sound):
        distance = self.object.getDistanceTo(self.cam)
        self.handle = self.device.play(sound)
        self.handle.volume = self.volume / distance
        
    def stop(self):
        self.handle.stop()
        
