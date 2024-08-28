import bge
from collections import OrderedDict

class spawn(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        for i in range(12):
            new = self.object.scene.addObject("Sword Skeleton", self.object)
            new.components['pathfinding'].tmp = i

    def update(self):
        pass
