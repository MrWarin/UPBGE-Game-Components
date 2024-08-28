import bge
import bpy
from collections import OrderedDict
from math import sin
from mathutils import Vector

class hud(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ('HUD ON/OFF', True)
    ])

    def start(self, args):
        self.hudOnOff = args['HUD ON/OFF']
        
        if self.hudOnOff == True:
            self.scene = self.object.scene
            hud = bpy.data.collections['HUD']
            self.hud_cam = self.scene.objects['HUD Camera']
            self.cam = self.scene.objects['Camera']
            
            self.hud_dict = dict()
            self.addObjectToHudDict()
#            self.hud_dict[self.scene.objects['Cube.001']] = None
            
            self.scene.addOverlayCollection(self.hud_cam, hud)
            
            self.messagebox = self.scene.objects['Message']
            self.message = bpy.data.objects['Message']
            self.messagebox.visible = False
            self.message.data.body = ""
            self.messageFt = 0
            
            self.ammoPanel = self.scene.objects['Ammo Panel']
            self.ammoType = self.scene.objects['Ammo Type']
            self.ammo = bpy.data.objects['Ammo']
            self.ammo.data.body = ""
            self.hideAll(self.ammoPanel)
            
            self.expPanel = self.scene.objects['Exp Panel']
            self.expPoint = bpy.data.objects['Exp Point']
            self.expText = bpy.data.objects['Exp Text']
            self.expPoint.data.body = ""
            self.expText.data.body = ""
            self.expTimer = 0
            self.hideAll(self.expPanel)
            
#            self.combobox = self.scene.objects['Combo Panel']
#            self.combo = bpy.data.objects['Combo Number']
#            self.hideAll(self.combobox)
#            self.comboFt = 0
            
            self.crosshair = self.scene.objects['Crosshair']
            self.crosshair_dynamic = self.scene.objects['Crosshair Dynamic']
            self.scope = self.scene.objects['Scope Overlay']
            self.hideAll(self.crosshair)
            self.hideAll(self.scope)
            
            self.cont = self.object.components['controller']
            self.move = self.object.components['movement']
#            self.hitpoint = bpy.data.objects['Hitpoint']
#            self.updateHP(self.cont.data['hp'], self.cont.data['maxhp'])
#            
#            self.hitbar = self.scene.objects['Health']
#            percent = self.cont.data['hp'] * 100 / self.cont.data['maxhp']
#            self.updateBar('Health', 0, percent)
#            
#            self.stabar = self.scene.objects['Stamina']
#            percent = self.cont.data['sp'] * 100 / self.cont.data['maxsp']
#            self.updateBar('Stamina', 0, percent)

    def update(self):
        if self.hudOnOff == True:
#            self.resetCombo()
            self.resetMessage()
            self.resetExp()
            self.setHudToObject()
            
    def resetExp(self):
        if self.expPanel.visible == True:
            if self.expTimer <= 0:
                self.hideAll(self.expPanel)
                return
            
            self.expTimer -= 0.1
            
    def startExp(self, point, text):
        self.expPoint.data.body = f"+{point}"
        self.expText.data.body = text
        self.expTimer = 10
        self.showAll(self.expPanel)
        
    def isOnScreen(self, coords):
        width = bge.render.getWindowWidth()
        height = bge.render.getWindowHeight()
        
        if (0 <= coords[0] <= width and 0 <= coords[1] <= height):
            return True
        else:
            return False
        
    def addObjectToHudDict(self):
        for object in self.scene.objects:
            if 'hud' in object:
                self.hud_dict[object] = None
            
    def setHudToObject(self):
        for ref, hud_object in self.hud_dict.items():
            screen_coords = self.cam.getScreenPosition(ref)
#            near_to_player = self.object.getDistanceTo(ref)
            is_on_screen = self.isOnScreen(screen_coords)
            
            if hud_object is None:
                hud_object = self.scene.addObject(f"event_{ref['hud']}", ref)
                self.hud_dict[ref] = hud_object
            
            if not is_on_screen or not self.move.interProp or ref != self.move.interProp[0]:
                self.hideAll(hud_object)
                continue
            
            self.showAll(hud_object)
            screen_vector = self.hud_cam.getScreenVect(*screen_coords)
            distance = self.hud_cam.worldPosition.z / screen_vector.z
            relative_position = distance * screen_vector
            hud_object.worldPosition = self.hud_cam.worldPosition - relative_position
            hud_object.worldOrientation = self.hud_cam.worldOrientation
    
    def resetMessage(self):
        if self.messagebox.visible == True:
            if self.messageFt <= 0:
                self.messagebox.visible = False
                return
            
            self.messageFt -= 0.1
    
    def updateMessage(self, text):
        self.message.data.body = text
        self.messagebox.visible = True
        self.messageFt = 10
        
    def resetCombo(self):
        if self.combobox.visible == True:
            if self.comboFt >= 20:
                self.hideAll(self.combobox)
                self.char.combo = 0
                return    
            
            self.comboFt += 0.1
            
    def updateCrosshairScale(self, scale):
        for i in self.crosshair_dynamic.children:
            self.object.scene.objects[f"Line {i.name}"].worldPosition = i.worldPosition
        scale = self.mapValue(scale)
        self.crosshair_dynamic.localScale = Vector([scale,scale,1])
        
    def mapValue(self, x, in_min=0.3, in_max=5, out_min=1, out_max=2):
        y = ((x - in_min) * (out_max - out_min) / (in_max - in_min)) + out_min
        return y
    
    def updateCombo(self, amt):
        self.combo.data.body = str(amt)
#        self.combobox.playAction('Combo', 0, 3, speed=1, play_mode=0)
        self.showAll(self.combobox)
        self.comboFt = 0
    
    def showOverlay(self, overlay, active=True):
        if active == True:
            self.showAll(overlay)
        else:
            self.hideAll(overlay)
    
    def updateHP(self, min, max):
        self.hitpoint.data.body = f"{min}/{max}"
    
    def updateBar(self, anim, fr, to):
        if anim == 'Health':
            self.hitbar.playAction(anim, fr, to, speed=10, play_mode=0)
        elif anim == 'Stamina':
            self.stabar.playAction(anim, fr, to, speed=10, play_mode=0)
            
    def hideAll(self, obj, ignore=""):
            obj.visible = False
            for x in obj.children:
                if ignore and obj.name == ignore[0] and x.name != ignore[1]:
                    continue
                else:
                    self.hideAll(x, ignore)
            
    def showAll(self, obj, ignore=""):
            obj.visible = True
            for x in obj.children:
                if ignore and obj.name == ignore[0] and x.name != ignore[1]:
                    continue
                else:
                    self.showAll(x, ignore)
            
    def updateAmmo(self, data):
        self.ammo.data.body = f"{data[0]} / {data[1]}"
        
    def updateAmmoType(self, data):
        if self.cont.aim.active:
            for child in self.ammoType.children:
                if child.name == data:
                    self.showAll(child)
                else:
                    self.hideAll(child)