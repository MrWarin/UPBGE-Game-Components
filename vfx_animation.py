import bge
from collections import OrderedDict

class vfx_animation(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Start Frame", 1),
        ("End Frame", 1),
        ("Speed", 1.0),
        ("Play Mode", 0)
    ])

    def start(self, args):
        self.start = args['Start Frame']
        self.end =  args['End Frame']
        self.speed = args['Speed']
        self.play_mode = args['Play Mode']
        
        self.object.playAction(f'{self.object.name}_action', self.start, self.end, speed=self.speed, layer=1, play_mode=self.play_mode)
        self.object.playAction(f'{self.object.name}_node', self.start, self.end, speed=self.speed, layer=2, play_mode=self.play_mode)
        for i in self.object.children:
            i.playAction(f'{self.object.name}_{i.name}_action', self.start, self.end, speed=self.speed, layer=1, play_mode=self.play_mode)
            i.playAction(f'{self.object.name}_{i.name}_node', self.start, self.end, speed=self.speed, layer=2, play_mode=self.play_mode)

    def update(self):
        pass
