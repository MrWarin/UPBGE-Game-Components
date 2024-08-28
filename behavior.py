import bge
from collections import OrderedDict

class behavior(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        self.object.alignAxisToVect((0, 1, 0), 1)
        self.object.alignAxisToVect((0, 0, 1), 2)

    def update(self):
        self.object.worldPosition = self.parent.worldPosition
        
