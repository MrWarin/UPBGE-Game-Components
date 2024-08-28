import bge
from pickle import load
from collections import OrderedDict

class controller(bge.types.KX_PythonComponent):
    args = OrderedDict([
    ])

    def start(self, args):
        self.deltatime = False
        self.lastKeyEvent = False
        self.lastKeyButton = False
        self.dbTrigger = False
        self.data = False
        self.getSaveData()
        self.getControlKeys()
        
        self.ragdoll = self.object.scene.objects['Armature'].components['ragdoll']

    def update(self):
        self.dt = 1/bge.logic.getAverageFrameRate()
        self.startRagdoll()
    
    def getSaveData(self):
        path = bge.logic.expandPath('//bin/save_data.bin')
        with open(path, "rb") as file:
            self.data = load(file)

    def getControlKeys(self):
        keyboard = bge.logic.keyboard.inputs
        mouse = bge.logic.mouse.inputs
        path = bge.logic.expandPath('//bin/setting_data.bin')
        
        with open(path, "rb") as file:
            key_bindings = load(file).get('key_binding', {})
        
        for key, value in key_bindings.items():
            setattr(self, key, eval(value))
            
    def isDoubleTap(self):
        ft = bge.logic.getFrameTime()
        diff = ft - self.lastKeyEvent
        button = self.lastKeyButton
        key = False
        
        JUST_ACTIVATED = bge.logic.KX_INPUT_JUST_ACTIVATED

        key_mapping = {
            self.forward.queue: "forward",
            self.back.queue: "back",
            self.left.queue: "left",
            self.right.queue: "right"
        }

        for queue, direction in key_mapping.items():
            if JUST_ACTIVATED in queue:
                key = direction
                break
        
        if self.dbTrigger:
            self.dbTrigger = False
            
        if key is not False:
            self.lastKeyEvent = ft
            self.lastKeyButton = key
            if key == button and diff <= 0.3:
                self.dbTrigger = True
            else:
                self.dbTrigger = False
            
        return self.dbTrigger
    
    def applyDamage(self, damage):
        print(damage)
        
    def startRagdoll(self):
        if self.objective.active and self.objective.activated:
            active = False if self.ragdoll.active else True
            self.ragdoll.active = active
            
    def isAttacked(self, damage):
        if self.actionState != self.state['Down']:
            max_hp = self.charStats['maxhp']
            current_hp = self.charStats['hp']
            new_hp = max(0, current_hp - damage)

            if new_hp <= 0:
                self.isDown()
            else:
                self.isHit()

            hp_ratio_before = current_hp / max_hp * 100
            hp_ratio_after = new_hp / max_hp * 100
            self.hud.updateHP(new_hp, max_hp)
            self.hud.updateBar('Health', hp_ratio_before, hp_ratio_after)
            self.charStats['hp'] = new_hp
            
    def spendStamina(self, point):
        max_sp = self.charStats['maxsp']
        current_sp = self.charStats['sp']
        new_sp = max(0, current_sp - point)
        
        if new_sp < 0:
            self.hud.updateMessage('Stamina is insufficient')
            return

        sp_ratio_before = current_sp / max_sp * 100
        sp_ratio_after = new_sp / max_sp * 100
        self.hud.updateBar('Stamina', sp_ratio_before, sp_ratio_after)
        self.charStats['sp'] = new_sp
        