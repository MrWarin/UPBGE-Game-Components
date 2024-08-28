import bge
#import bpy
import pickle
from mathutils import Matrix
from collections import OrderedDict
#from pathlib import Path

class handhold(bge.types.KX_PythonComponent):
    
    args = OrderedDict([
        ("Handhold ON/OFF", True)
    ])

    def start(self, args):
        self.hanOnOff = args['Handhold ON/OFF']
        
        self.cont = self.object.components['controller']
        self.shoot = self.object.components['shooting']
        
#        if self.hanOnOff:
            # Load Object
#            self.arm = self.object.children['Armature']
#            self.hand_L = self.arm.channels['Hand.Hold.L']
#            self.hand_R = self.arm.channels['Hand.Hold.R']
#            self.bone = (self.hand_R, self.hand_L)
#            self.handaxis = ('RightHandHold', 'LeftHandHold')
        if self.hanOnOff:
            self.loadout = 0
            self.loadObject()
#            if self.loadout:
                # Get Armature's hand hold bone
#                self.holding = self.object.components['movement'].charStats['holding']
#                self.switchHandGrip()
                
    def update(self):
        if self.hanOnOff:
            self.startSwap()
#            self.animHandHold()
                        
    def animHandHold(self):
        # Update Location and Rotation along to each hand hold bones
        if self.loadout:
            for i, name in enumerate(self.loadout[self.holding]['item']):
#                    if name in self.object.scene.objects:
#                        object = self.object.scene.objects[name]
#                        mat = self.arm.worldTransform @ self.bone[i].pose_matrix
#                        loc, rot, sca = mat.decompose()
#                        mat_out = Matrix.LocRotScale(loc, rot, object.worldScale)
#                        object.worldTransform = mat_out
#  
                if self.loadout[self.holding]['anim']:
                    anim = self.loadout[self.holding]['anim']
                    arm = object.children[0]
                    arm.playAction(anim[0], anim[1], anim[2], speed=1, play_mode=1)
                        
    def getItemData(self):
        list = []
        data = self.cont.data
        loadout = data['loadout']
        holding = data['holding']
        if loadout:
#            path = Path(__file__).parent.parent.absolute()
            path = bge.logic.expandPath('//')
            with open(f"{path}/bin/equipment_data.bin", "rb") as file:
                data = pickle.load(file)
            
            for item in loadout: 
                if item in data.keys():
                    list.append({
                        "name": item,
                        "item": data[item]['item'],
                        "type": data[item]['type'],
                        "range": data[item]['range'],
                        "scope": data[item]['scope'],
                        "anim": data[item]['anim'],
                        "damage": data[item]['damage'],
                        "accuracy": data[item]['accuracy'],
                        "repeat": data[item]['repeat'],
                        "shot": data[item]['shot'],
                        "firerate": data[item]['firerate'],
                        "reload": data[item]['reload'],
                        "recoil": data[item]['recoil'],
                        "round": data[item]['round'],
                        "ammo": data[item]['ammo']
                    })
                    
            return list, holding
        return False
    
    def loadObject(self):
        # Load object from asset blend file
        loadout, holding = self.getItemData()
        if loadout:
            for key, obj in enumerate(loadout):
                for i, j in enumerate(obj['item']):
                    spawn = "RightHandHold" if i == 0 else "LeftHandHold" 
                    item = self.object.scene.addObject(f"{j}", spawn)
                    item.visible = True if key == holding else False
                    loadout[key]['item'][i] = item.name
            
            self.arm = self.object.children['Armature']
            self.hand_L = self.arm.channels['Hand.Hold.L']
            self.hand_R = self.arm.channels['Hand.Hold.R']
            self.holding = holding
            self.loadout = loadout
            
            self.switchHandGrip()
            self.showObject()
            
        return False
    
#    def loadObject(self):
#        # Load object from asset blend file
#        loadout = self.getItemData()
#        if loadout:
#            for obj in loadout:
#                if not obj in self.object.scene.objects:
#                    file = f"//assets/objects/{obj['name']}.blend"
#                    with bpy.data.libraries.load(file, link=True) as (fr, to):
#                        to.objects = fr.objects
#                        to.actions = fr.actions
#                    
#                    # Set all object ot game object
#                    tmp = []
#                    for obj_data in to.objects:
#                        tmp.append((obj_data, obj_data.parent))
#                        obj_data.parent = None
#                        bpy.data.collections["Collection"].objects.link(obj_data)
#                        self.object.scene.convertBlenderObject(obj_data)
#                        
##                    for act_data in to.actions:
##                        print(act_data)
#                    
#                    # Pairing parent and child
#                    for obj_data in tmp:
#                        if obj_data[1] != None:
#                            child = self.object.scene.objects[obj_data[0].name]
#                            parent = self.object.scene.objects[obj_data[1].name]
#                            child.setParent(parent)
#            return loadout
#        return False
    
#    def swapHandhold(self, num):
#        data = self.object.components['movement'].charStats
#        name = data['loadout'][data['holding']]
#        self.holding = data['holding']
#        self.holding = num
#        self.switchHandGrip()
#        self.showObject()
            
    def switchHandGrip(self):
        if self.loadout[self.holding] != None:
            if self.loadout[self.holding]['type'] == "Bow":
                self.bone = (self.hand_L, self.hand_R)
                self.handaxis = ('LeftHandHold', 'RightHandHold')
            else:
                self.bone = (self.hand_R, self.hand_L)
                self.handaxis = ('RightHandHold', 'LeftHandHold')
            
    def showObject(self):
        for key, name in enumerate(self.loadout):
            for num, item in enumerate(name['item']):
                obj = self.object.scene.objects[item]
                visible = True if key == self.holding else False
                obj.visible = visible
                self.recursiveShowObject(obj.children, visible)
                
                if visible:
                    obj.setParent(self.object.scene.objects[self.handaxis[num]])
                    mat = self.arm.worldTransform @ self.bone[num].pose_matrix
                    loc, rot, sca = mat.decompose()
                    mat_out = Matrix.LocRotScale(loc, rot, obj.worldScale)
                    obj.worldTransform = mat_out
                
    def recursiveShowObject(self, object, visible):
        if object != None:
            for obj in object:
                self.object.scene.objects[obj.name].visible = visible
                self.recursiveShowObject(obj.children, visible)
        else:
            return
        
    def startSwap(self):
        for i in range(1, 6):
            numkey = getattr(self.cont, f"num{i}")
            if numkey.active and numkey.activated:
                num = i-1
                if self.holding != num:
                    self.holding = num
                    self.switchHandGrip()
                    self.showObject()
                    self.shoot.getData()
                    break