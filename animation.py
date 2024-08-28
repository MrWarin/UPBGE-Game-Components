import bge
from collections import OrderedDict

class animation(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Animation ON/OFF", True),
        ("Animation Speed", 1.0)
    ])

    def start(self, args):
        self.aimOnOff = args['Animation ON/OFF']
        self.animSpeed = args['Animation Speed']
        self.arm = self.object.children["Armature"]
        self.actionProp = {}

    def update(self):
        self.applyAction()
    
    def applyAction(self):
        for layer, actionProp in list(self.actionProp.items()):
            action = actionProp[0]
            start = actionProp[1]
            end = actionProp[2]
            mode = actionProp[3]
            priority = actionProp[4]
            blendin = actionProp[5]
            speed = self.animSpeed

            self.arm.playAction(action, start, end, speed=speed, play_mode=mode, priority=priority, layer=layer, blendin=blendin, blend_mode=1)
            del self.actionProp[layer]
            
    def stopAction(self, layer):
        self.arm.stopAction(layer)
            
    def getActionData(self, layer):
        frame = self.arm.getActionFrame(layer)
        name = self.arm.getActionName(layer)
        return name, frame
