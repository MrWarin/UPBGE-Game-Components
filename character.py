import bge, bpy
import pickle
from mathutils import Matrix
from collections import OrderedDict
from pathlib import Path

class handhold(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        # Put your initialization code here, args stores the values from the UI.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.
        
        self.handhold = self.getItemData()
        
        if self.handhold:
            
            # Get Armature's hand hold bone
            self.arm = self.object.children["Armature"]
            
            if self.handhold["type"] == "Bow":
                self.bone = (self.arm.channels["Hand.Hold.L"], self.arm.channels["Hand.Hold.R"])
            else:
                self.bone = (self.arm.channels["Hand.Hold.R"], self.arm.channels["Hand.Hold.L"])
            
            # Load object from asset blend file
            filepath = f"//assets/objects/{self.handhold['name']}.blend"
            with bpy.data.libraries.load(filepath, link=True) as (data_from, data_to):
                data_to.objects = data_from.objects
                
            # Set all object ot game object
            for name in self.handhold["item"]:
                object = bpy.data.objects.get(name)
                bpy.data.collections["Collection"].objects.link(object)
                self.object.scene.convertBlenderObject(object)
                
    def update(self):
        # Put your code executed every logic step here.
        # self.object is the owner object of this component.
        # self.object.scene is the main scene.
        
        # Update Location and Rotation along to each hand hold bones
        if self.handhold:
            for i, name in enumerate(self.handhold["item"]):
                object = self.object.scene.objects[name]
                mat = self.arm.worldTransform @ self.bone[i].pose_matrix
                loc, rot, sca = mat.decompose()
                mat_out = Matrix.LocRotScale(loc, rot, object.worldScale)
                object.worldTransform = mat_out
                
    def getItemData(self):
        # Load data from save file
        path = Path(__file__).parent.parent.absolute()
        
#        with open(f"{path}/bin/save_data.bin", "rb") as file:
#            save_data = pickle.load(file)
        save_data = {
            "holding": 0,
            "loadout": ["Dark Spear", "Feather Dagger"]
        }
        
        name = save_data["loadout"][save_data["holding"]]
            
        if name:
        
            with open(f"{path}/bin/equipment_data.bin", "rb") as file:
                item = pickle.load(file)
                
            if name in item.keys():
                return {
                    "name": name,
                    "item": item[name]["item"],
                    "type": item[name]["type"]
                }
                
        return False
    
#    def swapHandHold(self):
#        self.handhold = {
#            "name": save_data["secondary"],
#            "item": item[save_data]["secondary"]]["item"],
#            "type": item[save_data]["secondary"]]["type"]
#        }