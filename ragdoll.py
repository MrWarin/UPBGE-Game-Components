# Created by Uniday Studio
import bge
import bpy
from collections import OrderedDict

from mathutils import Vector, Matrix

LINEAR_VELOCITY_GAIN = 40


class RagdollTimer():
    #Medidor de tempo!
    def __init__(self, initialTime=0):
        self._timer = 0
        self.reset()

        self._timer -= initialTime

    def reset(self):
        self._timer = bge.logic.getRealTime()

    def getElapsedTime(self):
        return bge.logic.getRealTime() - self._timer

    def get(self):
        return bge.logic.getRealTime() - self._timer

class ragdoll(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Active", True),
        ("Time", 0.5),
        ("Lerp Root Transform", 0.5),
    ])
    
    active = False

    def start(self, args):
        self.active = args["Active"]
        self.time  = args["Time"]
        
        self.__rootLerp = args["Lerp Root Transform"]
        
        self.__timer = RagdollTimer(self.time)
        self.__status = self.active
        self.__statusTap = 0
        
        # Force initial behavior
        for bone in bpy.data.objects[self.object.name].pose.bones:
            if 'Copy Transforms' in bone.constraints:
                bone.constraints['Copy Transforms'].influence = self.active
            if 'IK' in bone.constraints:
                bone.constraints['IK'].influence = 0
#            if 'Copy Location' in bone.constraints:
#                bone.constraints['Copy Location'].influence = 0
            if 'Transformation' in bone.constraints:
                bone.constraints['Transformation'].influence = 0
            
#        for obj in self.object.constraints:
#            print(obj)
#            obj.influence = float(self.active)
                        
        self.__startList = []        
        # Storing the initial transforms of the ragdoll objects
        tmpTransform = self.object.worldTransform
#        for obj in self.object.constraints:
        for obj in bpy.data.objects[self.object.name].pose.bones:
            out = [None, None]
            if 'Copy Transforms' in obj.constraints:
                cons = obj.constraints['Copy Transforms']
                if cons.target:
    #                target = cons.target.parent
                    target = self.object.scene.objects[cons.target.name]
                    transf = tmpTransform * target.worldTransform
                    out = [target, transf]
                    target.suspendPhysics()
                    self.__startList.append(out)
            
        self.__boneObjects = {}
        for (obj, _) in self.__startList:
            if obj:
                self.__boneObjects[obj.name] = obj
            
        # The root (parent) object
        self.__root = self.object
        while self.__root.parent:
            self.__root = self.__root.parent
            
        rCenter = self.getRagdollCenterTransform()
        self.__rootOffset = rCenter * self.__root.worldTransform
        
    def _getObjectName(self, bone):
        return "RagdollPart-" + self.object.name + "-" + bone.name + "-Dynamic"
    
    def getRagdollCenterTransform(self):
        transforms = [obj.worldTransform for (obj, _) in self.__startList if obj]
#        
#        count = 1       
        out = Matrix.Identity(4)
#        for t in transforms:
#            factor = 1.0 / count
#            out = out.lerp(t, factor)
#            count += 1
##        print(out)
        return out
    
    def getRagdollCenterPosition(self):
        pos = Vector([0,0,0])
        count = 0
        
        for (obj, _) in self.__startList:
            if obj:
                pos += obj.worldPosition
                count +=1
        
        if count > 0:
            pos /= count
            return pos
        return self.__root.worldPosition
    
    def resetRootTransform(self):
        # Reset to the ragdoll center
        center = self.getRagdollCenterPosition()
#        center += Vector([0,0,-1.42])
        
#        center += self.__rootOffset
        
        
#        cBoxMinZ = abs(self.__root.cullingBox.min.z * self.__root.worldScale.z)
#        target = center - Vector([0,0,cBoxMinZ])
        
        self.__root.worldPosition = center
        
#        hit, pos, _ = self.__root.rayCast(target, center, 0.0, "", 1, 1, 0, mask=1)
#        if hit:
#            self.__root.worldPosition.z = pos.z + cBoxMinZ
    
    def resetRagdollTransform(self):
        transform = self.object.worldTransform        
        for channel in self.object.channels:
            bone = channel.bone
            objName = self._getObjectName(bone)
            if objName in self.__boneObjects:
                obj = self.__boneObjects[objName]
#                pivot = obj.children[0]
#                pivot = obj
                
#                pivotSpace = pivot.worldTransform.inverted() * obj.worldTransform
                
#                obj.worldTransform = transform * (channel.pose_matrix * pivotSpace)
                
                obj.linearVelocity = [0,0,10]
                obj.angularVelocity = [0,0,10]
#                obj.applyForce(Vector([0,0,0]))
                            
    def applyLinearVelocity(self):
        character = bge.constraints.getCharacter(self.__root)
        
        if character:
            dir = character.walkDirection
            
            for (obj, _) in self.__startList:
                if obj:
                    obj.setLinearVelocity(dir * LINEAR_VELOCITY_GAIN)
                  
    def run(self):
        if self.__status != self.active:
            self.__status = self.active
            self.__timer.reset()
            
            if self.active:
                self.__root.suspendPhysics()
#                self.__statusTap = 0
#                self.resetRagdollTransform()
#                self.resetRootTransform()
                self.applyLinearVelocity()

                for (obj,_) in self.__startList:
                    obj.restorePhysics()
            else:
                self.__root.restorePhysics()
                for (obj,_) in self.__startList:
                    obj.suspendPhysics()
            
#        t = self.__timer.get() / self.time
#        if t <= 1.5:
#            if not self.active: t = 1.0 - t
#            t = min(1.0, max(0.0, t))
#            print(t)
        t = 1 if self.active else 0
        d = 0 if t else 1
            
        for bone in bpy.data.objects[self.object.name].pose.bones:
#                for const in bone.constraints:
#                    const.influence = t
            if 'Copy Transforms' in bone.constraints:
                bone.constraints['Copy Transforms'].influence = t
            if 'IK' in bone.constraints:
                bone.constraints['IK'].influence = d
#            if 'Copy Location' in bone.constraints:
#                bone.constraints['Copy Location'].influence = d
            if 'Transformation' in bone.constraints:
                bone.constraints['Transformation'].influence = d
#            for obj in self.object.constraints:
#                print(obj)
#                obj.influence = t
                
        if self.active:
            pass
#            self.__statusTap += 1
#            if self.__statusTap > 2:
#                self.object.update()
            
            self.resetRootTransform()
        else:
#            pass
#            if t > 1.0:
            for obj in bpy.data.objects[self.object.name].pose.bones:
                if 'Copy Transforms' in obj.constraints:
                    cons = obj.constraints['Copy Transforms']
                    if cons.target:
                        bone_pose_matrix = self.object.channels[obj.name].pose_matrix
                        armature_world_matrix = self.object.worldTransform
                        bone_world_matrix = armature_world_matrix @ bone_pose_matrix
    
                        target = self.object.scene.objects[cons.target.name]
                        target.worldTransform = bone_world_matrix
                
#                self.resetRagdollTransform()
    
    def update(self):
        self.run()

