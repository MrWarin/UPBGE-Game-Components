import bge
import pickle
from collections import OrderedDict
from pathlib import Path
from math import ceil
from random import randint

class none_player(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ('Trace ON/OFF', True),
        ('Attack ON/OFF', True)
    ])

    def start(self, args):
        self.traOnOff = args['Trace ON/OFF']
        self.attOnOff = args['Attack ON/OFF']
        
#        self.arm = self.object.children[0]
        self.NearToEnemy = self.object.sensors['NearCharacter']
        self.pathfinding = self.object.components['pathfinding']
#        self.collision = self.object.children[0].children[0].sensors['Collision']
        
        self.action = {
            "Skeleton_Run": 0,
            "Sword_Skeleton_Normal_Attack": 0,
            "Sword_Skeleton_Heavy_Attack": 0
        }
        
#        self.charStats = self.getCharacterData()
        self.actionProp = 0
        self.actionState = 0
        self.animSpeed = 1
        self.attackProp = 0
        self.attackFt = 0
        self.attackType = 0
        self.attackTmp = 0
        self.attackHit = 0

    def update(self):
        if self.traOnOff == True:
            self.resetTrace()
            self.startTrace()
            
        if self.attOnOff == True:
            self.resetAttack()
            self.startAttack()
        
#        self.applyAction()
        
#        self.Idle()
        
    def Idle(self):
        if self.actionState == 0:
            self.actionProp = ('Skeleton_Idle', 1, 20, 1, 99)
            
    def resetTrace(self):
        if self.actionState == 1:
            self.actionProp = ('Skeleton_Run', 10, 1, 0, 0)
            self.actionState = 0
        
    def startTrace(self):
#        hitObjectList = self.NearToEnemy.hitObjectList
#        if hitObjectList:
#            dist, world, local = self.object.getVectTo(hitObjectList[0])
#            if dist > 2:
#                self.object.alignAxisToVect(world, 1, 0.25)
#                self.object.alignAxisToVect((0, 0, 1), 2)
#                self.object.applyMovement((0, 0.02, 0), 1)
        if self.pathfinding.getRunProp():
            if self.actionState == 0:
                self.actionProp = ('Skeleton_Run', 1, 10, 0, 0)
                self.actionState = 1
            if self.actionState == 1:
                self.actionProp = ('Skeleton_Run', 10, 60, 1, 1)
                
    def resetAttack(self):
        if self.actionState == 2:
            self.actionState = 0
    
    def startAttack(self):
        if self.pathfinding.getAttackProp():
            
            if not self.attackType:
                self.attackType = "Normal_Attack" if randint(0, 4) else "Heavy_Attack"
                self.attackProp = 0 if self.attackProp >= len(self.charStats[self.attackType.lower()]) else self.attackProp
                self.attackProp = 0 if self.attackTmp != self.attackType else self.attackProp
            
            start, end, hit = self.charStats[self.attackType.lower()][self.attackProp]
            ft = bge.logic.getFrameTime() - self.attackFt
        
            if ft > 1:
                action = f"{self.object.name.replace(' ', '_')}_{self.attackType}"
                self.actionProp = (action, start, end, 0, 0)
                self.actionState = 2
                
            if self.actionState == 2:
                if start == self.action[action]:
                    self.attackHit = 0
                    
                if hit-2 < self.action[action] < hit+2 and not self.attackHit and self.collision.positive:
                    self.attackHit = 1
                    target = self.collision.hitObject
                    damage = 100
                    target.components['movement'].isAttacked(damage)
                
                if end-5 < self.action[action] < end:
                    self.actionProp = 0
                    self.actionState = 0
                    self.action[action] = 0
                    self.attackFt = bge.logic.getFrameTime()
                    self.attackProp += 1
                    self.attackTmp = self.attackType
                    self.attackType = 0
                
    def applyAction(self):
        if self.actionProp:
            frame = self.arm.getActionFrame()
            name = self.arm.getActionName()
            self.action[name] = frame
            
            action = self.actionProp[0]
            start = self.actionProp[1]
            end = self.actionProp[2]
            mode = self.actionProp[3]
            priority = self.actionProp[4]
            
            self.arm.playAction(action, start, end, speed=self.animSpeed, play_mode=mode, priority=priority, blendin=7)
            self.resetAction(name)
    
    def resetAction(self, name):
        for i in self.action:
            if name != i and self.action[i] > 0:
                self.action[i] = 0
            
    def getCharacterData(self):
        path = Path(__file__).parent.parent.absolute()
        with open(f"{path}\\bin\\character_data.bin", "rb") as file:
            data = pickle.load(file)
            
        return data[self.object.name]
