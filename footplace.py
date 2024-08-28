import bge
import bpy
from math import radians
from mathutils import Vector, Matrix
from collections import OrderedDict

class footplace(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Footplace ON/OFF", True),
        ("Foot Smooth", 0.2),
        ("Hip Smooth", 0.2)
    ])

    def start(self, args):
        self.footOnOff = args['Footplace ON/OFF']
        self.smoothF = args['Foot Smooth']
        self.smoothH = args['Hip Smooth']
        
        self.ground = 'Pelvis'
        self.target = self.object.worldPosition.copy()
        self.scene = self.object.scene
        
        self.footplace_H = bpy.data.objects["Armature"].pose.bones["Hip"].constraints["Copy Location"]
        self.footplace_L = bpy.data.objects["Armature"].pose.bones["FootLeft"].constraints["Copy Location"]
        self.footplace_R = bpy.data.objects["Armature"].pose.bones["FootRight"].constraints["Copy Location"]
        
#        self.object.disableRigidBody()
#        self.object.gravity.z=-12
        
        for obj in self.object.children:
            if 'Armature' in obj.name:
                self.arm = obj
        
    def update(self):
#        angle_y = radians(0)
#        angle_z = radians(180)

#        # Calculate rotation matrices for the Y and Z axes
#        rotation_matrix_y = Matrix.Rotation(angle_y, 4, 'Y')
#        rotation_matrix_z = Matrix.Rotation(angle_z, 4, 'Z')

        # Combine the rotations
#        current_rotation = self.object.worldOrientation @ rotation_matrix_z.to_3x3()
#        rotation_matrix = current_rotation @ rotation_matrix_y.to_3x3()
        
        # Update the object's orientation using the new Y-axis vector
#        self.arm.worldOrientation = rotation_matrix.to_quaternion()
        
        if self.footOnOff:
#            climb = 0
#            if hasattr(self.object.components['movement'], 'climbProp'):
#                climb = self.object.components['movement'].climbProp
            
#            if not climb:
            # CALL FUNCTION
            lFoot = self.Foot('FootLeft', 'Foot.L' , 1.2, 0.4, [0,1,0], self.smoothF)
            rFoot = self.Foot('FootRight','Foot.R', 1.2, 0.4, [1,0,0], self.smoothF)
            hips  = self.Foot('Hip', self.ground, 1.2, 0.4, [0,1,0], self.smoothH)
                    
            # SET HIP POSITION
            if lFoot[1] and rFoot[1]:
                if lFoot[1].z < rFoot[1].z:
                    self.ground = 'Foot.L'                             
            
                if rFoot[1].z < lFoot[1].z:
                        self.ground = 'Foot.R'

    def Foot(self, sensor, bone, lengh, height, color, speed):
        self.sensor = self.scene.objects.get(sensor) 
        self.bone = self.arm.channels[bone]        
       
        # BONE POSITION
        bonePos = self.arm.worldPosition + (self.arm.worldOrientation @ ((self.bone.pose_head * self.arm.worldScale.x) + Vector([0, 0, height])))
        to = bonePos - (self.object.worldOrientation @ Vector([0, 0, lengh]))
        
        # RAYCAST    
        obj,hit,norm = self.object.rayCast(to, bonePos, xray=1, mask=0x0001)
        
        if hit:
            # Rotate X axis of sensor along to floor's normal.
            self.sensor.alignAxisToVect(norm, 2, 0.1)
                                  
            self.target = hit
            dist = hit - bonePos
#            bge.render.drawLine(bonePos,hit,color)
            
#            self.arm.channels['Foot.R'].location = (0,0,0)
            self.arm.update()
            
            # CONSTRAINTS
#            for cons in self.arm.constraints:
#                if 'IK' in cons.name or 'Transformation' in cons.name:
#                    cons.influence = 0
        else:
#            bge.render.drawLine(bonePos,to,color)
            dist = to - bonePos
            self.target.z = self.arm.worldPosition.z
            
#            for cons in self.arm.constraints:
#                if 'IK' in cons.name or 'Transformation' in cons.name:
#                    cons.influence = 0
        
        smooth = self.sensor.worldPosition.lerp(self.target, speed)
        self.sensor.worldPosition = smooth
        
        return dist, hit
    
    def enable(self):
        self.footplace_H.influence = 1
        self.footplace_L.influence = 1
        self.footplace_R.influence = 1
        self.footOnOff = True
        
    def disable(self):
        self.footplace_H.influence = 0
        self.footplace_L.influence = 0
        self.footplace_R.influence = 0
        self.footOnOff = False