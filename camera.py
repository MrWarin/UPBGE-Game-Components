import bge
import bpy
from mathutils import Matrix, Vector
from math import radians, cos, pi
from collections import OrderedDict

class camera(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Camera Look ON/OFF", True),
        ("Aim ON/OFF", True),
        ("Look ON/OFF", True),
        ("Collision ON/OFF", True),
        ("Collision Speed", 0.05),
        ("Collision Distance", 0.05),
        ("Movement ON/OFF", True),
        ("Movement Speed", 0.05),
        ("Rotation ON/OFF", True),
        ("Rotation Speed", 0.05),
        ("X", True),
        ("Y", True),
        ("Z", True),
        ("X Angle", -10.0),
        ("Y Angle", 0.0),
        ("Z Angle", 0.0)
    ])

    def start(self, args):
        # Mandatory Attribute
        self.parent = self.object.parent
        self.move = self.parent.components['movement']
        self.shoot = self.parent.components['shooting']
        self.cont = self.parent.components['controller']
        self.camera = self.object.children['Camera']
        self.arm = self.parent.children['Armature']
        self.camSide = "R"
        self.aimPoint = self.object.children[f'AimPoint.{self.camSide}']
        self.camPoint = self.object.children[f'CamPoint.{self.camSide}']
        self.zoomPoint = self.object.scene.objects[f'ZoomPoint.{self.camSide}']
        self.camSensitive = 0.002
        self.focalLength = [30, 200, 600]
        self.camSensitiveList = [0.002, 0.0002, 0.00002]
#        self.camPoint = self.camPoint.worldPosition
#        self.direction = self.object.scene.objects['Direction']
#        self.direction.removeParent()
#        self.arm = self.object.scene.objects['Armature']
#        self.arm.removeParent()
        self.screen_x = bge.render.getWindowWidth() // 2
        self.screen_y = bge.render.getWindowHeight() // 2
        bge.render.setMousePosition(self.screen_x, self.screen_y)
        
        # Camera Look:
        self.camOnOff = args['Camera Look ON/OFF']
        
        # Movement Attribute
        self.movOnOff = args['Movement ON/OFF']
        self.movSpeed = args['Movement Speed']
        self.bone = self.arm.channels['Pelvis']
        self.col_bone = self.arm.channels['Head']
        self.object.removeParent()
        
        # Rotation Attribute
        self.rotOnOff = args['Rotation ON/OFF']
        self.mouse = self.object.sensors['Mouse']
        self.rotSpeed = args['Rotation Speed']
        self.x = args['X']
        self.y = args['Y']
        self.z = args['Z']
        self.origin_x = args['X Angle']
        self.origin_y = args['Y Angle']
        self.origin_z = args['Z Angle']
        self.timer = 0.0
            
        # Collision Attribute
        self.colOnOff = args['Collision ON/OFF']
        self.colSpeed = args['Collision Speed']
        self.colDistance = args['Collision Distance']
#        self.minPoint = self.object.children['MinPoint']
        
        # Zoom Attribute
        self.aimOnOff = args['Aim ON/OFF']
        self.lookOnOff = args['Look ON/OFF']
        self.head = bpy.data.objects["Armature"].pose.bones["Head"].constraints["Track To"]
        self.neck = bpy.data.objects["Armature"].pose.bones["Neck"].constraints["Track To"]
        self.chest = bpy.data.objects["Armature"].pose.bones["Torso"].constraints["Copy Rotation"]
        self.aimtimer = 0.0

    def update(self):
        # Mouselook
        if self.camOnOff:
            self.mouseLook()
        
        # Movement
        if self.movOnOff:
            self.movement()        
            
        # Rotation
        if self.rotOnOff:
            self.rotation()
            
        # Collision
        if self.colOnOff:
            self.collision()
            
        # Aim
        if self.aimOnOff:
            self.startAim()
            self.startZoom()
            
        # Look At
        if self.lookOnOff:
            self.lookAt()
            
    def mouseLook(self):
        movement = Vector(self.mouse.position)
        center = Vector((self.screen_x, self.screen_y))
        offset = (movement - center) * self.camSensitive
        min = radians(-75)
        max = radians(60)
        
        angle = self.object.worldOrientation.to_euler()
        
        self.object.applyRotation([0, 0, -offset.x], 0)
        if (angle.x >= min and offset.y > 0) or (angle.x <= max and offset.y < 0):
            self.object.applyRotation([-offset.y, 0, 0], 1)
            self.mouseMove = True
        else:
            self.mouseMove = False
            
        bge.render.setMousePosition(self.screen_x, self.screen_y)
        
    def switchLook(self, side="R"):
        if side:
            self.camSide = side
        self.aimPoint = self.object.children[f'AimPoint.{side}']
        self.camPoint = self.object.children[f'CamPoint.{side}']
        self.zoomPoint = self.object.scene.objects[f'ZoomPoint.{self.camSide}']
                
    def movement(self):
#        slowM = Vector.lerp(self.object.localPosition, self.parent.localPosition, self.movSpeed)
        bone = self.arm.worldPosition + (self.arm.worldOrientation @ (self.bone.pose_head))
        slowM = Vector.lerp(self.object.worldPosition, bone, self.movSpeed)
        self.object.localPosition = slowM
    
    def rotation(self):
        self.timer += 0.02
        target = self.parent.worldOrientation
        
        if self.x == True and self.origin_x != 0:
            target = target @ Matrix.Rotation(radians(self.origin_x), 3, 'X')
        if self.y == True and self.origin_y != 0:
            target = target @ Matrix.Rotation(radians(self.origin_y), 3, 'Y')
        if self.z == True and self.origin_z != 0:
            target = target @ Matrix.Rotation(radians(self.origin_z), 3, 'Z')
            
        slowR = Matrix.lerp(self.object.worldOrientation, target, self.rotSpeed)            
        rot = self.object.worldOrientation.to_euler()
        
        if self.x == True:
            rot[0] = slowR.to_euler()[0]            
        if self.y == True:
            rot[1] = slowR.to_euler()[1]
        if self.z == True:
            rot[2] = slowR.to_euler()[2]
        
        if not self.mouseMove:
            if self.timer > 1 and self.move.runProp:
                self.object.worldOrientation = rot.to_matrix()                  
        else:
            self.timer = 0
            
    def collision(self):
        if not self.shoot.zoomPoint:
            self.camSensitive = self.camSensitiveList[0]
            self.camera.lens = self.focalLength[0]
            
            aim_position = self.aimPoint.worldPosition if self.cont.aim.active else self.camPoint.worldPosition
            
            offset = self.arm.worldOrientation @ Vector([0, 1, 0])
            bone = self.arm.worldPosition + (self.arm.worldOrientation @ (self.col_bone.pose_head)) + offset
            hit_object, hit_point, _ = self.object.rayCast(aim_position, bone, xray=1, mask=0x0001)
            
            target_position = hit_point if hit_object else aim_position
                
            self.camera.worldPosition = Vector.lerp(self.camera.worldPosition, target_position, 0.3)
        
    def startAim(self):
        if self.cont.aim.active:
            vec = self.camera.worldOrientation.col[0].to_3d()
            self.rotateAim(vec)
#            slowA = Vector.lerp(self.camera.worldPosition, self.aimPoint.worldPosition, 0.5)
#            self.camera.worldPosition = slowA
#            self.aimtimer = 1
            
#            rot = self.object.worldOrientation.to_euler()
#            self.torso.rotation_mode = bge.logic.ROT_MODE_XYZ
#            self.torso.rotation_euler = [-rot.x, 0, 0]
#            self.arm.update()
#        else:
#            if self.aimtimer > 0:
#                slowA = Vector.lerp(self.camera.worldPosition, self.camPoint.worldPosition, 0.7)
#                self.camera.worldPosition = slowA
#                self.aimtimer -= 0.2

    def rotateAim(self, vec):
        self.parent.alignAxisToVect(vec, 0, 0.3)
        self.parent.alignAxisToVect((0, 0, 1), 2, 1)
        
    def startZoom(self):
        if self.shoot.zoomPoint:
            self.camera.worldPosition = self.zoomPoint.worldPosition
            self.camSensitive = self.camSensitiveList[self.shoot.zoomPoint]
            if self.camera.lens < self.focalLength[self.shoot.zoomPoint]:
                self.camera.lens = min(self.focalLength[self.shoot.zoomPoint], self.camera.lens + 1800 * self.cont.dt)
            else:
                self.camera.lens = max(self.focalLength[self.shoot.zoomPoint], self.camera.lens - 1800 * self.cont.dt)
            
    def lookAt(self):
        diff = self.object.worldOrientation.col[1]
        dot = diff.dot(self.parent.worldOrientation.col[1])
        threshold = 0.1
        influence_change = 0.1
    
        if dot < threshold:
            self.head.influence = max(0, self.head.influence - influence_change)
            self.neck.influence = max(0, self.neck.influence - influence_change)
            self.chest.influence = max(0, self.chest.influence - influence_change)
        else:
            self.head.influence = min(1, self.head.influence + influence_change)
            self.neck.influence = min(1, self.neck.influence + influence_change)
            self.chest.influence = min(1, self.chest.influence + influence_change)
            
    def enable(self):
        self.lookOnOff = True
        diff = self.object.worldOrientation.col[1]
        dot = diff.dot(self.parent.worldOrientation.col[1])
        threshold = 0.1
        if dot > threshold:
            self.head.influence = 1
            self.neck.influence = 1
            self.chest.influence = 1
        
    def disable(self):
        self.lookOnOff = False
        self.head.influence = 0
        self.neck.influence = 0
        self.chest.influence = 0