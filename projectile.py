import bge
from mathutils import Vector
from collections import OrderedDict

class projectile(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
        ("Animation", "wiggle"),
        ("Start Frame", 1),
        ("End Frame", 20),
        ("VFX", "Water Splash"),
        ("VFX Start Frame", 1),
        ("VFX end Frame", 30)
    ])

    def start(self, args):
        self.anim = args['Animation']
        self.start = args['Start Frame']
        self.end = args['End Frame']
        self.vfx = args['VFX']
        self.vfx_start = args['VFX Start Frame']
        self.vfx_end = args['VFX end Frame']
        
        self.anim = self.anim.split(',')

    def update(self):
        self.deltatime = 1/bge.logic.getAverageFrameRate()
        self.resetProjectile()
        self.startProjectile()
        
    def resetProjectile(self):
        if not self.point_list:
            self.object.endObject()
    
    def startProjectile(self):
        for i, v in enumerate(self.anim):
            self.object.playAction(v, self.start, self.end, play_mode=1, layer=i)
#        self.object.applyRotation(Vector([0, 0, 0.25]))
        
        if self.point_list:
#            for i in range(len(self.point_list) - 1):
#                bge.render.drawLine(self.point_list[i], self.point_list[i+1], [1,0,0])
            
            nextPosition = self.point_list[1] if len(self.point_list) > 1 else self.point_list[0]
#            bge.render.drawLine(nextPosition, self.object.worldPosition, [1,0,0])
            hit, hitPosition, normal = self.object.rayCast(nextPosition, self.object.worldPosition, 0.7)
            if hit:
                self.hitObject(hit, hitPosition, normal)
                return
            
            diff = nextPosition - self.object.worldPosition
            
            if diff.length > 0.01:
                factor = min(1.0, (0.25) * self.deltatime / diff.length)
                inter = self.object.worldPosition.lerp(nextPosition, factor)
                movement = inter - self.object.worldPosition
                self.object.worldPosition += movement
                self.object.alignAxisToVect(movement, 1)
            else:
                self.point_list.pop(0)
                
    def hitObject(self, name, position, normal):
        add = self.object.scene.addObject(self.vfx, self.object, self.vfx_end)
        add.alignAxisToVect(normal, 2)
        self.object.endObject()
        
        if name['npc'] == "enemy":
            self.direction = self.direction * 500
            print(self.direction)
#            name.endObject()
            
