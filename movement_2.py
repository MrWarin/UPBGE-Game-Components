import bge
import bpy
from collections import OrderedDict
from mathutils import Vector, Matrix
from math import ceil, cos, sin, degrees, radians 
    
class movement(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Movement ON/OFF", True),
        ("Walk Speed", 0.05),
        ("Run Speed", 0.1),
        ("Crouch ON/OFF", True),
        ("Jump ON/OFF", True),
        ("Climb ON/OFF", True),
        ("Dodge ON/OFF", True)
    ])

    def start(self, args):
        self.movOnOff = args['Movement ON/OFF']
        self.walkSpeed = args['Walk Speed']
        self.runSpeed = args['Run Speed']
        self.croOnOff = args['Crouch ON/OFF']
        self.jumOnOff = args['Jump ON/OFF']
        self.cliOnOff = args['Climb ON/OFF']
        self.dodOnOff = args['Dodge ON/OFF']
        
        # Lgic Brick Sensors
        self.cam = self.object.scene.objects['Camera']
        self.camLook = self.object.scene.objects['Camera Look']
#        self.NearToEnemy = self.object.sensors["NearToEnemy"]
#        self.RayToEnemy = self.object.sensors["RayToEnemy"]
        self.arm = self.object.children["Armature"]
        
        # Components
        self.hud = self.object.components['hud']
        self.anim = self.object.components['animation']
        self.cont = self.object.components['controller']
        self.shoot = self.object.components['shooting']

        # Constraint
        self.character = bge.constraints.getCharacter(self.object)
        self.head = bpy.data.objects["Armature"].pose.bones["Neck"].constraints["Track To"]
        self.hand_L = bpy.data.objects["Armature"].pose.bones["Hand.IK.L"].constraints["Copy Location"]
#        self.torso = bpy.data.objects["Armature"].pose.bones["Torso"].constraints["Track To"]
        
        # Footplace
#        self.footplace_Root = bpy.data.objects["Armature"].pose.bones["Root"].constraints["Copy Location"]
        self.footplace_L = bpy.data.objects["Armature"].pose.bones["FootLeft"].constraints["Copy Location"]
        self.footplace_R = bpy.data.objects["Armature"].pose.bones["FootRight"].constraints["Copy Location"]
        
        # Movement Prop
        self.moveProp = 1
        self.runProp = 0
        self.leapProp = 0
        self.dodgeProp = 0
        self.dodging = 0
        self.dodgeVector = 0
        self.jumpFt = 0
        self.stateTmp = 0

        # Climb Prop
        self.climbProp = 0
        self.snapProp = 0
        self.wallProp = 0
        self.topProp = 0
        self.bottomProp = 0
        self.floorProp = 0
        self.edgeProp = 0
        self.headProp = 0
        self.edgeFt = 0
        self.tmpProp = 0
        self.midProp = 0
        
        # Attack Prop
        self.chargeProp = 0
        self.attackProp = 0
        self.aimProp = 0
        self.attackFt = 0
        self.attackMx = 3
        self.targetProp = 0
        self.targetFt = 0
        self.targetPos = (0, 0)
        self.guardFt = 0
        self.attacking = 0
        
        # Anim Prop
        self.actionState = 0
        self.ragdoll = True
        
        self.interProp = 0
        
        # Other Prop
#        self.lastKeyEvent = 0
#        self.lastKeyButton = 0
#        self.dbTrigger = 0
#        self.aimtimer = 0
        # 'forward', 'left', 'back', 'right'
        self.vector_mapping = {
            (True, False, False, False): ([0, 0.1, 0], 0, 1),
            (False, True, False, False): ([-0.1, 0, 0], 1.5708, 2),
            (False, False, True, False): ([0, -0.1, 0], 3.14159, 3),
            (False, False, False, True): ([0.1, 0, 0], -1.5708, 4),
            (True, True, False, False): ([-0.1, 0.1, 0], 0.785398, 5),
            (True, False, False, True): ([0.1, 0.1, 0], -0.785398, 6),
            (False, True, True, False): ([-0.1, -0.1, 0], 2.35619, 7),
            (False, False, True, True): ([0.1, -0.1, 0], -2.35619, 8)
        }
        
        # Action Frame Property
#        self.action = {
#            "Idle": 0,
#            "Walk": 0,
#            "Walk_Left": 0,
#            "Walk_Back": 0,
#            "Walk_Right": 0,
#            "Walk_ForwardLeft": 0,
#            "Walk_ForwardRight": 0,
#            "Walk_BackLeft": 0,
#            "Walk_BackRight": 0,
#            "Sneak": 0,
#            "Run": 0,
#            "Run_Left": 0,
#            "Run_Back": 0,
#            "Run_Right": 0,
#            "Run_ForwardLeft": 0,
#            "Run_ForwardRight": 0,
#            "Run_BackLeft": 0,
#            "Run_BackRight": 0,
#            "Jump": 0,
#            "Leap": 0,
#            "IdleToClimb": 0,
#            "IdleToClimb_Down": 0,
#            "Climb": 0,
#            "Aim": 0,
#            "Down": 0,
#            "Hit":0,
#            "RunToIdle_R": 0,
#            "RunToIdle_L": 0,
#            "Charge": 0,
#            "Attack_M2": 0
#        }
        
        # Action State Indicator
        self.state = {
            "Idle": 0,
            "Walk": 1,
            "Run": 2,
            "Crouch": 3,
            "Sneak": 4,
            "Jump": 5, 
            "Dodge": 6,
            "Climb": 7, 
            "Guard": 8,
            "Aim": 9,
            "Attack": 10,
            "Charge": 11,
            "Down": 12,
            "Hit": 13
        }
        
#        self.getControlKeys()
#        self.RunStateList = [
#            self.state['Idle'], 
#            self.state['Guard'],
#            self.state['Walk'],
#            self.state['Run'], 
#            self.state['Jump'], 
#            self.state['Crouch'], 
#            self.state['Sneak']
#        ]
#        self.combo = 0

    def update(self):
        self.deltatime = 1/bge.logic.getAverageFrameRate()
        
#        if self.ragdoll:
#            return
        
        self.Idle()
        
        if self.movOnOff == True:
            self.resetRun()
            self.startRun()
            
        if self.cliOnOff == True:
            self.resetClimb()
            self.startClimb()
            
        if self.jumOnOff == True:
            self.resetJump()
            self.startJump()
        
        if self.croOnOff == True:
            self.resetCrouch()
            self.startCrouch()
            
        if self.dodOnOff == True:
            self.resetDodge()
            self.startDodge()
            
        self.startInteract()
            
#        if self.aimOnOff == True:
#            self.resetAim()
#            self.startAim()
            
#        if self.attOnOff == True:
#            self.resetHit()
#            self.resetAttack()
##            self.leapAttack()
#            self.startAttack()
            
#        if self.tarOnOff == True:
#            self.resetTarget()
##            self.detectTarget()
#            self.startTarget()
            
#        if self.swaOnOff == True:
#            self.startSwap()
            
        # Reset State
#        self.resetTarget()
#        self.resetAttack()
#        self.resetClimb()
#        self.resetJump()
#        self.resetRun()
        
#        fromVec = self.object.worldPosition.copy()
#        toVec = fromVec + Vector((0, 1, 0))
#        bge.render.drawLine(fromVec, toVec, [1.0, 0.0, 0.0])
#        print(self.object.rayCast(toVec, fromVec, 2, "wall")[0], self.RayToWall.hitObject)
        
        # events on Keyboard or Mouse
#        self.startRun()
#        self.jumpUp()
#        self.SwitchIdleToCrouch()
#        self.switchTo()
#        self.attackTo()
            
        # Object Detector
#        self.leapAttack()
#        self.detectTarget()
#        self.detectWall()
        
        # Action Update
#        self.aimTarget()
#        self.RunToIdle()
#        self.IdleOnWall()

#        print(self.root_vec)
#        new_position = self.root.worldPosition.lerp(self.object.worldPosition - (self.camLook.worldOrientation @ Vector([0, self.root_vec, 0])), 0.1)
#        self.root.worldPosition = new_position

#        self.applyAction()
        
    # -------------------------------------------------------------
    # Start of Idle Action
        
    def Idle(self):
        if self.actionState == self.state['Idle']:
            self.anim.actionProp[1] = ("Idle", 0, 72, 1, 99, 1, 7)
        
        elif self.actionState == self.state['Crouch']:
            self.anim.actionProp[1] = ("Crouch", 30, 90, 1, 99, 1, 7)
            
#        elif self.actionState == self.state['Guard']:
#            self.actionProp[1] = ("Guard", 30, 90, 1, 99, 1, 7)
            
#        elif self.actionState == self.state['Down']:
#            self.anim.actionProp[1] = ("Down", 60, 100, 1, 99, 1, 7)
    
    # End of Idle Action
    # -------------------------------------------------------------
    # Start of Crouch Action
    
    def resetCrouch(self):
        if self.actionState == self.state['Crouch']:
            if not self.cont.crouch.active:
                self.actionState = self.state['Idle']
                self.anim.actionProp[1] = ("Crouch", 30, 1, 0, 1, 1, 7)
              
    def startCrouch(self):
        if self.actionState == self.state['Idle']:
            if not self.climbProp and self.cont.crouch.active:
                self.actionState = self.state['Crouch']
                self.anim.actionProp[1] = ("Crouch", 1, 30, 0, 1, 1, 7)
            
    # End of Crouch Action
    # -------------------------------------------------------------
    # Start of Run Action
                    
    def resetRun(self):
        if not any([self.cont.forward.active, self.cont.back.active, self.cont.left.active, self.cont.right.active]):
            self.runProp = 0
            name, frame = self.anim.getActionData(1)
            
            # Reset run state
            if self.actionState in [self.state['Walk'], self.state['Run']]:
                self.actionState = self.state['Idle']
                priority = 1 if name == "Leap" and frame > 59 else 2
                action = "RunToIdle_R" if name == "Run" and (50 <= frame <= 75 or 15 <= frame <= 28) else "RunToIdle_L"
                self.anim.actionProp[1] = (action, 1, 56, 0, priority, 1, 7)
                
            # Reset sneak state
            if self.actionState == self.state['Sneak']:
                self.actionState = self.state['Crouch']
                action = "RunToIdle_R" if name == "Sneak" and (30 <= frame <= 60 or 15 <= frame <= 28) else "RunToIdle_L"
                self.anim.actionProp[1] = (action, 1, 56, 0, 2, 1, 7)
                    
#    def startRun(self):
#        if self.forward.active:
##            vec = self.object.getVectTo("FaceFront")
#            vector = Vector([0, 0.1, 0])
#            runAnim = 1
#        elif self.left.active:
##            vec = self.object.getVectTo("FaceLeft")
#            vector = Vector([-0.1, 0, 0])
#            runAnim = 2
#        elif self.back.active:
##            vec = self.object.getVectTo("FaceBack")
#            vector = Vector([0, -0.1, 0])
#            runAnim = 3
#        elif self.right.active:
##            vec = self.object.getVectTo("FaceRight")
#            vector = Vector([0.1, 0, 0])
#            runAnim = 4
#            
#        if self.forward.active and self.left.active:
##            vec = self.object.getVectTo("FaceFrontLeft")
#            vector = Vector([-0.1, 0.1, 0])
#            runAnim = 5
#        elif self.forward.active and self.right.active:
##            vec = self.object.getVectTo("FaceFrontRight")
#            vector = Vector([0.1, 0.1, 0])
#            runAnim = 6
#        elif self.back.active and self.left.active:
##            vec = self.object.getVectTo("FaceBackLeft")
#            vector = Vector([-0.1, -0.1, 0])
#            runAnim = 7
#        elif self.back.active and self.right.active:
##            vec = self.object.getVectTo("FaceBackRight")
#            vector = Vector([0.1, -0.1, 0])
#            runAnim = 8
#            
#        if (self.forward.active or self.back.active or self.left.active or self.right.active):
#            self.runProp = runAnim
#            self.leapProp = 0
#            self.moveTo(vector)
            
    def startRun(self):
        for condition, (vector, radians, runAnim) in self.vector_mapping.items():
            if all(getattr(self.cont, direction).active == active for direction, active in zip(('forward', 'left', 'back', 'right'), condition)):
                self.runProp = runAnim
                self.leapProp = 0
                self.shoot.isAccurate = min(5, self.shoot.isAccurate + 0.6)
                self.moveTo(Vector(vector), radians)
                return
                
    def moveTo(self, vector, radians):
        if not self.moveProp:
            return
        
        if self.cont.isDoubleTap():
            self.dodgeVector = (vector, self.runProp)
            self.actionState = self.state['Dodge']
            return
        
        if not self.cont.aim.active and self.cont.sprint.active and self.cont.sprint.activated:
            self.actionState = self.state['Run']
            
        actions = None
        name, frame = self.anim.getActionData(1)
        
        # Walk State
        if self.actionState in [self.state['Idle'], self.state['Walk']]:
            self.actionState = self.state['Walk']
            self.stateTmp = self.actionState
            priority = 1 if name == "Jump" and frame > 59 else 2
            actions = {
                1: ("Walk", 1, 17, 0, priority, 1, 7),
                2: ("Walk_Left", 1, 17, 0, priority, 1, 7),
                3: ("Walk_Back", 1, 17, 0, priority, 1, 7),
                4: ("Walk_Right", 1, 20, 0, priority, 1, 7),
                5: ("Walk_ForwardLeft", 1, 17, 0, priority, 1, 7),
                6: ("Walk_ForwardRight", 1, 21, 0, priority, 1, 7),
                7: ("Walk_BackLeft", 1, 20, 0, priority, 1, 7),
                8: ("Walk_BackRight", 1, 20, 0, priority, 1, 7)
            }
            
            if (
                (name == "Walk" and frame > 14) or 
                (name == "Walk_Left" and frame > 14) or 
                (name == "Walk_Back" and frame > 14) or 
                (name == "Walk_Right" and frame > 14) or 
                (name == "Walk_ForwardLeft" and frame > 14) or 
                (name == "Walk_ForwardRight" and frame > 14) or 
                (name == "Walk_BackLeft" and frame > 14) or 
                (name == "Walk_BackRight" and frame > 14)
            ):
                actions = {
                    1: ("Walk", 17, 68, 1, 2, 1, 7),
                    2: ("Walk_Left", 17, 68, 1, 2, 1, 7),
                    3: ("Walk_Back", 17, 68, 1, 2, 1, 7),
                    4: ("Walk_Right", 17, 68, 1, 2, 1, 7),
                    5: ("Walk_ForwardLeft", 17, 68, 1, 2, 1, 7),
                    6: ("Walk_ForwardRight", 17, 68, 1, 2, 1, 7),
                    7: ("Walk_BackLeft", 17, 68, 1, 2, 1, 7),
                    8: ("Walk_BackRight", 17, 68, 1, 2, 1, 7)
                }
            
        # Run State
        if self.actionState in [self.state['Run']]:
            if self.cont.aim.active:
                self.actionState = self.state['Idle']
            
            self.stateTmp = self.actionState
            priority = 1 if name == "Jump" and frame > 59 else 2
            actions = {
                1: ("Run", 1, 52, 0, priority, 1, 7),
#                2: ("Run_Left", 1, 20, 0, priority, 1, 7),
                2: ("Run", 1, 52, 0, priority, 1, 7),
#                3: ("Run_Back", 1, 12, 0, priority, 1, 7),
                3: ("Run", 1, 52, 0, priority, 1, 7),
#                4: ("Run_Right", 1, 20, 0, priority, 1, 7),
                4: ("Run", 1, 52, 0, priority, 1, 7),
#                5: ("Run_ForwardLeft", 1, 21, 0, priority, 1, 7),
                5: ("Run", 1, 52, 0, priority, 1, 7),
#                6: ("Run_ForwardRight", 1, 21, 0, priority, 1, 7),
                6: ("Run", 1, 52, 0, priority, 1, 7),
#                7: ("Run_BackLeft", 1, 20, 0, priority, 1, 7),
                7: ("Run", 1, 52, 0, priority, 1, 7),
#                8: ("Run_BackRight", 1, 20, 0, priority, 1, 7)
                8: ("Run", 1, 52, 0, priority, 1, 7)
            }
            
            if (
                (name == "Run" and frame > 49) or 
                (name == "Run_Left" and frame > 18) or 
                (name == "Run_Back" and frame > 9) or 
                (name == "Run_Right" and frame > 18) or 
                (name == "Run_ForwardLeft" and frame > 18) or 
                (name == "Run_ForwardRight" and frame > 18) or 
                (name == "Run_BackLeft" and frame > 17) or 
                (name == "Run_BackRight" and frame > 17)
            ):
                actions = {
                    1: ("Run", 52, 102, 1, 2, 1, 7),
#                    2: ("Run_Left", 21, 70, 1, 2, 1, 7),
                    2: ("Run", 52, 102, 1, 2, 1, 7),
#                    3: ("Run_Back", 12, 56, 1, 2, 1, 7),
                    3: ("Run", 52, 102, 1, 2, 1, 7),
#                    4: ("Run_Right", 21, 70, 1, 2, 1, 7),
                    4: ("Run", 52, 102, 1, 2, 1, 7),
#                    5: ("Run_ForwardLeft", 21, 70, 1, 2, 1, 7),
                    5: ("Run", 52, 102, 1, 2, 1, 7),
#                    6: ("Run_ForwardRight", 21, 70, 1, 2, 1, 7),
                    6: ("Run", 52, 102, 1, 2, 1, 7),
#                    7: ("Run_BackLeft", 20, 65, 1, 2, 1, 7),
                    7: ("Run", 52, 102, 1, 2, 1, 7),
#                    8: ("Run_BackRight", 20, 65, 1, 2, 1, 7)
                    8: ("Run", 52, 102, 1, 2, 1, 7)
                }
                
        # Sneak State
        if self.actionState in [self.state['Crouch'], self.state['Sneak']]:
            self.actionState = self.state['Sneak']
            self.stateTmp = self.actionState
            actions = {
                1: ("Sneak", 1, 30, 0, 1, 1, 7),
                2: ("Sneak_Left", 1, 20, 0, 1, 1, 7),
                3: ("Sneak_Back", 1, 12, 0, 1, 1, 7),
                4: ("Sneak_Right", 1, 20, 0, 1, 1, 7),
                5: ("Sneak_ForwardLeft", 1, 21, 0, 1, 1, 7),
                6: ("Sneak_ForwardRight", 1, 21, 0, 1, 1, 7),
                7: ("Sneak_BackLeft", 1, 20, 0, 1, 1, 7),
                8: ("Sneak_BackRight", 1, 20, 0, 1, 1, 7)
            }
            
            if (
                self.action["Sneak"] > 49 or 
                self.action["Sneak_Left"] > 18 or 
                self.action["Sneak_Back"] > 9 or 
                self.action["Sneak_Right"] > 18 or 
                self.action["Sneak_ForwardLeft"] > 18 or 
                self.action["Sneak_ForwardRight"] > 18 or 
                self.action["Sneak_BackLeft"] > 17 or 
                self.action["Sneak_BackRight"] > 17
            ):
                actions = {
                    1: ("Sneak", 52, 102, 1, 2, 1, 7),
                    2: ("Sneak_Left", 21, 70, 1, 2, 1, 7),
                    3: ("Sneak_Back", 12, 56, 1, 2, 1, 7),
                    4: ("Sneak_Right", 21, 70, 1, 2, 1, 7),
                    5: ("Sneak_ForwardLeft", 21, 70, 1, 2, 1, 7),
                    6: ("Sneak_ForwardRight", 21, 70, 1, 2, 1, 7),
                    7: ("Sneak_BackLeft", 20, 65, 1, 2, 1, 7),
                    8: ("Sneak_BackRight", 20, 65, 1, 2, 1, 7)
                }
        
        if actions:
            self.anim.actionProp[1] = actions.get(self.runProp)
        
        # Turn and move
        if self.stateTmp == self.state['Run']:
            spd = self.runSpeed
            rot = self.camLook.worldOrientation @ self.camLook.worldOrientation.Rotation(radians, 3, 'Z')
        else:
            spd = self.walkSpeed
            rot = self.camLook.worldOrientation
            
        loc = self.camLook.worldOrientation @ vector
#        loc_vec = self.object.worldOrientation @ loc_vec
        loc.z = 0
        self.object.worldPosition = self.object.worldPosition + loc.normalized() * spd
        self.trackTo(rot, 0.15)
        
    def trackTo(self, rot, factor):
        # Lerp the rotation for each axis
#        self.object.alignAxisToVect(rot, 1, factor)
        self.object.worldOrientation = self.object.worldOrientation.lerp(rot, factor)
        self.object.alignAxisToVect([0, 0, 1], 2, 1)
        
#    def RunToIdle(self):
#        if 1 < self.action["RunToIdle_R"] < 28:
#            self.object.applyMovement((0, 0.01, 0), 1)
#        if 29 < self.action["RunToIdle_R"] < 56:
#            self.object.applyMovement((0, 0.002, 0), 1)
            
    # End of Run Action
    # -------------------------------------------------------------  
    # Start of Jump Action
            
#    def resetJump(self):
#        if self.actionState == self.state['Jump']:
#            
#            self.jumpFt += 1*self.deltatime
#            
#            if self.character.onGround:
#                if self.stateTmp == self.state['Run']:
#                    self.actionProp[1] = ("Leap", 60, 119, 0, 1, 1, 7)
#                    self.actionState = self.state['Run']
#                elif self.stateTmp == self.state['Walk']:
#                    self.actionProp[1] = ("Jump", 60, 119, 0, 1, 1, 7)
#                    self.actionState = self.state['Walk']
#                else:
#                    self.actionProp[1] = ("Jump", 60, 119, 0, 1, 1, 7)
#                    self.actionState = self.state['Idle']
#                
##                if self.jumpFt > 1:
##                    damage = ceil(100 * self.jumpFt)
##                    print(f"Fall Damage: {damage}")
##                    self.isAttacked(damage)
#                    
#                self.jumpFt = 0
#            else:
#                if self.action["Jump"] > 59 or self.action["Leap"] > 59:
#                    self.actionProp[1] = ("Jump", 58, 58, 1, 1, 1, 7)
#            
#    def startJump(self):
#        if self.actionState in [self.state['Idle'], self.state['Run'], self.state['Walk'], self.state['Jump']]:
#            if not self.wallProp and self.moveProp and self.jump.active and self.jump.activated:
#                
#                if self.character.onGround:
#                    if self.actionState == self.state['Idle']:
#                        self.actionProp[1] = ("Jump", 1, 60, 0, 1, 1, 7)
#                    else:
#                        self.actionProp[1] = ("Leap", 1, 60, 0, 2, 1, 7)
#                else:
#                    if self.character.jumpCount < self.character.maxJumps:
#                        self.actionProp[1] = ("Leap", 1, 60, 0, 1, 1, 7)

#                self.character.jump()
#                self.stateTmp = self.actionState
#                self.actionState = self.state['Jump']
                
    def resetJump(self):
        if self.actionState == self.state['Jump']:
            self.jumpFt += 1 * self.deltatime
            
            if self.character.onGround:
                if self.stateTmp == self.state['Run']:
                    self.anim.actionProp[1] = ("Leap" if self.stateTmp == self.state['Run'] else "Jump", 60, 119, 0, 1, 1, 7)
                    self.actionState = self.stateTmp
                else:
                    self.anim.actionProp[1] = ("Jump", 60, 119, 0, 1, 1, 7)
                    self.actionState = self.state['Idle']
                
#                if self.jumpFt > 1:
#                    damage = ceil(100 * self.jumpFt)
#                    print(f"Fall Damage: {damage}")
#                    self.isAttacked(damage)
                    
                self.jumpFt = 0
            else:
                name, frame = self.anim.getActionData(1)
                if (name == "Jump" and frame > 59) or (name == "Leap" and frame > 59):
                    self.anim.actionProp[1] = ("Jump", 58, 58, 1, 1, 1, 7)

    def startJump(self):
        if self.actionState in [self.state['Idle'], self.state['Run'], self.state['Walk'], self.state['Jump']]:
            if not self.wallProp and self.moveProp and self.cont.jump.active and self.cont.jump.activated:
                if self.character.onGround:
                    self.anim.actionProp[1] = ("Jump" if self.actionState == self.state['Idle'] else "Leap", 1, 60, 0, 1 if self.actionState == self.state['Idle'] else 2, 1, 7)
                elif self.character.jumpCount < self.character.maxJumps:
                    self.anim.actionProp[1] = ("Leap", 1, 60, 0, 1, 1, 7)
                    
                self.character.jump()
                self.stateTmp = self.actionState
                self.actionState = self.state['Jump']

    # End of Jump Action
    # -------------------------------------------------------------
    # Start of Climb Action
    
    def resetClimb(self):
        if self.actionState == self.state['Climb']:
            # Cancel climb
            if self.climbProp == 0:
                self.moveProp = 1
                self.tmpProp = 0
                self.object.restorePhysics()
                if self.floorProp:
                    self.anim.actionProp[1] = ("Jump", 60, 119, 0, 0, 1, 7)
                    self.actionState = self.state['Idle']
            
            # Drop down
            if self.climbProp == 2 and self.cont.back.active and self.cont.back.activated:
                if self.bottomProp:
                    self.climbProp = 5
                else:
                    self.climbProp = 0
                
            if self.climbProp == 2:
                self.object.suspendPhysics(1)
            
                self.anim.actionProp[1] = ("IdleToClimb", 60, 60, 0, 0, 1, 7)
                self.midProp = 0
                self.tmpProp = 0
            
            if self.climbProp == 2 and self.cont.forward.active and self.cont.forward.activated:
                # Check if character is hanging on the top of building
                _, hit, norm = self.topProp
                diff = hit.z - (self.object.worldPosition.z + 1.45)
                if diff > 0.1:
                    self.climbProp = 1
                else:
                    self.climbProp = 3
            
            # When top of builing
            if self.climbProp == 3:
                self.actionState = self.state['Climb']
                self.object.suspendPhysics(1)
                
                if self.midProp:
                    self.anim.actionProp[1] = ("ClimbToIdle_Mid", 1, 80, 0, 0, 1, 7)
                else:
                    self.anim.actionProp[1] = ("ClimbToIdle", 1, 140, 0, 0, 1, 7)

                hitH = self.headProp[1] if self.headProp else 0
                if hitH:
                    self.climbProp = 2
                    return
                
                hitT = self.topProp[1] if self.topProp else 0
                if hitT:
                    diff = hitT - (self.object.worldPosition + Vector([0,0,-1.4]))
                    if diff.z > 0.1:
    #                    inter = self.object.worldPosition.lerp(hit - Vector([0,0,-1.42]), 0.8*self.deltatime)
    #                    self.object.worldPosition.z = inter.z
                        
                        self.object.worldPosition.z += 2*self.deltatime
                    else:
                        if not self.tmpProp:
                            self.tmpProp = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.75,0]))
                            
                        diff = self.object.worldPosition - self.tmpProp
                        if self.tmpProp and diff.length > 0.1:
                            self.object.worldPosition = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,2*self.deltatime,0]))
                        else:
                            self.tmpProp = 0
                            self.climbProp = 0
#                        if not self.snapProp:
#                            pos = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.8,0]))
#                            self.snapProp = ((None, pos, -self.object.worldOrientation.col[1]), 0)
                else:
                    self.climbProp = 0

    def startClimb(self):
        self.detectWall()
        self.detectEdge()
        self.detectCorner()
        self.detectFloor()
        
        # Detect wall
        if self.actionState == self.state['Idle']:
            if self.wallProp and self.cont.jump.active and self.cont.jump.activated:
                self.snapProp = (self.wallProp, None, 1)
            
        if self.snapProp:
             self.snapTo()
             
        if self.climbProp == 1:
            self.actionState = self.state['Climb']
            
            self.anim.actionProp[1] = ("IdleToClimb", 1, 60, 0, 0, 1, 7)
            
            name, frame = self.anim.getActionData(1)
            if name == "IdleToClimb" and frame > 24:
                _, hit, norm = self.tmpProp if self.tmpProp else self.topProp
                if not self.tmpProp:
                    self.tmpProp = self.topProp
                
                if hit:
                    # Bypass to step 3 if wall is not higher than character's height
                    top = (self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0,3]))) - hit
                    if top.z > 2:
                        mid = hit - self.object.worldPosition
                        if mid.z > 0.1:
                            self.object.worldPosition.z += 3*self.deltatime
                        else:
                            self.midProp = 1
                            self.tmpProp = 0
                            self.climbProp = 3
                        return
                    
                    diff = hit - (self.object.worldPosition + Vector([0,0,1.4]))
                    if diff.z > 0.1:
        #                inter = self.object.worldPosition.lerp(hit - Vector([0,0,1.42]), 0.1)
        #                self.object.worldPosition.z = inter.z

                        self.object.worldPosition.z += 3*self.deltatime
                    else:
                        self.climbProp = 2
                else:
                    self.climbProp = 0
        
        if self.climbProp == 4:
            self.actionState = self.state['Climb']
            self.arm.removeParent()
#            self.footplace_Root.influence = 0
            self.footplace_R.influence = 0
            self.footplace_L.influence = 0
            self.object.suspendPhysics(1)
            
            self.anim.actionProp[1] = ("IdleToClimb_Down", 1, 120, 0, 0, 1, 7)
                
#            if self.action['IdleToClimb_Down'] >= 100:
            name, frame = self.anim.getActionData(1)
            if name == "IdleToClimb_Down" and frame > 100:
#                hit = self.topProp[1] if self.topProp else 0
                
                edge = self.edgeProp if self.edgeProp else 0
                floor = self.floorProp if self.floorProp else 0
                
#                self.object.worldPosition = edge[0]
                self.object.worldPosition = Vector([edge[0].x, edge[0].y, floor[1].z]) + Vector([0,0,-1.4])
                self.object.alignAxisToVect(-edge[1], 1, 1)
                self.object.alignAxisToVect((0, 0, 1), 2, 1)
                
                vec = self.object.worldPosition
                self.arm.worldPosition = Vector([vec[0], vec[1], vec[2] - 1.4])
                self.arm.alignAxisToVect(edge[1], 1, 1)
                self.arm.alignAxisToVect((0, 0, 1), 2, 1)
                self.arm.setParent(self.object)
                
#                self.footplace_Root.influence = 1
                self.footplace_R.influence = 1
                self.footplace_L.influence = 1
#                
                self.anim.actionProp[1] = ("IdleToClimb", 60, 60, 0, 0, 1, 0)
                self.climbProp = 2
                
#            if self.action['IdleToClimb_Down'] > 17:
            if name == "IdleToClimb_Down" and frame > 50:
                edge = self.edgeProp if self.edgeProp else 0
                floor = self.floorProp if self.floorProp else 0
                if edge:
#                    pos = 0
#                    rot = 0
#                    diff = self.object.worldOrientation.col[1]
#                    dot = diff.dot(-edge[1])
#                    threshold = 0.997
#                    if dot < threshold:
#                        self.object.applyRotation([0, 0, -5*self.deltatime])
#                    else:
#                        rot = 1
                    destination = Vector([edge[0].x, edge[0].y, floor[1].z]) + Vector([0,0,-1.4])
                    diff = destination - self.object.worldPosition
                    if diff.length > 0.1:
                        displacement = diff.normalized() * (3*self.deltatime)
                        self.object.worldPosition += displacement
#                        pos = 1
                    
#                    if pos:
#                        self.edgeProp = 0
#                else:
#                    hit = self.topProp[1] if self.topProp else 0
#                    if hit:
#                    diff = edge[0] - (self.object.worldPosition)
#                    if self.floorProp:
#                        self.climbProp = 0
#                        return
                    
#                    if diff.z < -0.001:
        #                inter = self.object.worldPosition.lerp(hit - Vector([0,0,1.42]), 0.1)
        #                self.object.worldPosition.z = inter.z
#                        self.object.worldPosition.z -= 3*self.deltatime
#                    else:
#                        self.climbProp = 2
#                    else:
#                        self.climbProp = 0
                
        if self.climbProp == 5:
            self.actionState = self.state['Climb']
            
            _, hit, norm = self.tmpProp if self.tmpProp else self.bottomProp
            if not self.tmpProp:
                self.tmpProp = self.bottomProp
            
            if hit:
                diff = hit - (self.object.worldPosition + Vector([0,0,1.4]))
                if self.floorProp:
                    self.climbProp = 0
                    return
                
                if diff.z < -0.1:
                    self.object.worldPosition.z -= 6*self.deltatime
                else:
                    self.climbProp = 2
            else:
                self.climbProp = 2
            
    def detectWall(self):
        length = 1 if self.climbProp else 1
        
        top = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,length,3]))
        target = top - Vector([0,0,5])
        bge.render.drawLine(top, target, [0,0,1])
        _, hitT, normT = self.object.rayCast(target, top, face=1, xray=1, prop='scene', mask=0x0001)
        
        if hitT:
            self.topProp = (_, hitT, normT)
        else:
            self.topProp = 0
            
#        bottom = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,length,1.4]))
#        target = bottom - Vector([0,0,5])
#        bge.render.drawLine(bottom, target, [0,0,1])
#        _, hitB, normB = self.object.rayCast(target, bottom, face=1, prop='scene', mask=0x0001)
#        
#        if hitB:
#            self.bottomProp = (_, hitB, normB)
#        else:
#            self.bottomProp = 0
        
        front = self.object.worldPosition + (self.object.worldOrientation.col[1])
        bge.render.drawLine(self.object.worldPosition, front, [0,0,1])
        _, hitW, normW = self.object.rayCast(front, None, xray=1, face=1, prop='scene', mask=0x0001)
        
        if hitW and hitT:
#            hitW = hitW + (self.object.worldOrientation @ Vector([0,-0.35,0]))
            tmp = hitW + (normW * Vector([0.4,0.4,0]))
            bge.render.drawLine(hitW, tmp, [1,1,0])
            self.wallProp = (_, tmp, normW)
        else:
            self.wallProp = 0
            
        head = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0,1.5]))
        target = head - self.object.worldOrientation @ Vector([0,-1,0])
        bge.render.drawLine(target, head, [0,0,1])
        _, hitH, normH = self.object.rayCast(target, head, face=1, prop='scene', mask=0x0001)
        
        if hitH:
            self.headProp = (_, hitH, normH)
        else:
            self.headProp = 0
        
    def detectEdge(self):
        if not self.climbProp and self.moveProp:
            if not self.runProp:
                self.edgeFt = 0
                
            mid = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.35,0]))
            target = mid - Vector([0,0,2])
            bge.render.drawLine(mid, target, [0,0,1])
            _, hitM, normM = self.object.rayCast(target, mid, face=1, prop='scene', mask=0x0001)
            
            rear = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.35,-2]))
            target = rear - self.object.worldOrientation @ Vector([0,0.1,0])
            bge.render.drawLine(rear, target, [0,0,1])
            _, hitR, normR = self.object.rayCast(rear, target, face=1, prop='scene', mask=0x0001)
        
            if not hitM and hitR and not self.bottomProp:
                # To prevent falling from edge
                pos = hitR + (self.object.worldOrientation @ Vector([0,-0.35,0]))
                self.object.worldPosition.x = pos.x
                self.object.worldPosition.y = pos.y
                
                if self.runProp:
                    self.edgeFt += self.deltatime
                    hitR = hitR + Vector([0, 0, -1.42])
                    tmp = hitR + (normR * Vector([0.4,0.4,0]))
                    bge.render.drawLine(hitR, tmp, [1,1,0])
                    
                if self.edgeFt > 0.5:
#                    self.edgeProp = (tmp, normR)
#                    self.actionProp[1] = ("IdleToClimb_L", 1, 60, 0, 0)
#                    self.moveProp = 0
#                    self.object.suspendPhysics(1)
#                    tmp = tmp + (self.object.worldOrientation @ Vector([0,0,-1.42]))
#                    tmp = hitR + (normR * Vector([0.35,0.35,-1.42]))
#                    tmp = tmp + Vector([0,0,-1.42])
                    self.edgeProp = (tmp, normR)
                    self.snapProp = ((_, self.object.worldPosition, -normR), None, 4)

    def detectCorner(self):
        pass
#        start = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.45,0]))
#        
#        right = start - self.object.worldOrientation @ Vector([-0.3,0,0])
#        bge.render.drawLine(start, right, [1,0,0])
#        _, hitR, normR = self.object.rayCast(right, start, face=1, prop='scene', mask=0x0001)
#        
#        left = start - self.object.worldOrientation @ Vector([0.3,0,0])
#        bge.render.drawLine(start, left, [0,1,0])
#        _, hitL, normL = self.object.rayCast(left, start, face=1, prop='scene', mask=0x0001)
#        
#        if hitR:
#            tmp = hitR + (normR * Vector([0.4,0.4,0]))
#            bge.render.drawLine(hitR, tmp, [1,1,0])
#        if hitL:
#            tmp = hitL + (normL * Vector([0.4,0.4,0]))
#            bge.render.drawLine(hitL, tmp, [1,1,0])
#                
    def detectFloor(self):
        below = self.object.worldPosition + Vector([0,0,-1.42])
        bge.render.drawLine(self.object.worldPosition, below, [0,0,1])
        _, hit, norm = self.object.rayCast(below, None, face=1)
        
        if hit:
            self.floorProp = (_, hit, norm)
        else:
            self.floorProp = 0
        
    def snapTo(self):
        self.object.suspendPhysics(1)
        self.moveProp = 0
        rot = 0
        pos = 0
        offset = Vector([0,0,0])
        _, hit, norm = self.snapProp[0]
        
        if self.snapProp[1]:
            offset = self.snapProp[1]
        
#        if self.snapProp[1]:
#            anim, start, end = self.snapProp[1]
#            self.anim.actionProp[1] = (anim, start, end, 0, 1, 0)
        
        if not hit or not norm:
            self.climbProp = 0
            self.snapProp = 0
            return
        
        if norm:
            diff = self.object.worldOrientation.col[1]
            dot = diff.dot(-norm)
            threshold = 0.9997
#                print(diff, dot, threshold)
            if dot < threshold:
#           if abs(diff.x) > 0.01 and abs(diff.y) > 0.01:
#                self.trackTo(-norm, 0.2)
                self.object.alignAxisToVect(-norm, 1, 0.2)
                self.object.alignAxisToVect([0, 0, 1], 2, 1)
            else:
                rot = 1

#                diff = hit - (self.object.worldPosition + (self.object.worldOrientation.col[1] / 3))
#                tmp = (self.object.worldPosition + (self.object.worldOrientation.col[1] / 3))
#                bge.render.drawLine(tmp, hit, [1,0,1])

        if hit:
            diff = hit - (self.object.worldPosition - offset)
#                print(hit, self.object.worldPosition, diff)
            if diff.length > 0.05:
                lerp = self.object.worldPosition.lerp(hit + offset, 0.2)
                self.object.worldPosition = lerp
            else:
                pos = 1
                
        if rot and pos:
#            self.object.restorePhysics()
            self.climbProp = self.snapProp[2]
            self.snapProp = 0
#            self.moveProp = 1
    
    def getCurveLine(self):
        distance = sqrt((self.point3.worldPosition.x - self.point1.worldPosition.x)**2 + (self.point3.worldPosition.y - self.point1.worldPosition.y)**2)
        factor = 0.1
        diff = distance * factor
        
        midpoint = (self.point1.worldPosition + self.point3.worldPosition) / 2
        
        self.point2.worldPosition = midpoint
        self.point2.worldPosition.z = max(self.point1.worldPosition.z, self.point3.worldPosition.z) + diff
        
        point_list = []

        for ratio in range(self.vertex_count + 1):
            ratio = ratio / self.vertex_count

            tangent_line_vertex1 = self.point1.worldPosition.lerp(self.point2.worldPosition, ratio)
#            bge.render.drawLine(self.point1.worldPosition, self.point2.worldPosition, [1,0,0])
            
            tangent_line_vertex2 = self.point2.worldPosition.lerp(self.point3.worldPosition, ratio)
#            bge.render.drawLine(self.point2.worldPosition, self.point3.worldPosition, [0,0,1])
            
            bezier_point = tangent_line_vertex1.lerp(tangent_line_vertex2, ratio)
#            bge.render.drawLine(tangent_line_vertex1, tangent_line_vertex2, [1,1,1])

            point_list.append(bezier_point)

#        for i in range(len(point_list) - 1):
#            bge.render.drawLine(point_list[i], point_list[i+1], [1,1,1])

    # End of Climb Action
    # -------------------------------------------------------------
    # Start of Dodge Action
    
    def resetDodge(self):
        if self.dodgeProp and not self.dodging:
            self.actionState = self.state['Idle']
            self.dodgeProp = 0
            self.moveProp = 1
        
    def startDodge(self):
        if self.actionState == self.state['Dodge']:
            
            self.dodgeProp = 1
            
            action = None
            dodgeMove = True
            name, frame = self.anim.getActionData(1)
            if (
                (name == "Dodge" and frame > 39) or 
                (name == "Dodge_Left" and frame > 39) or 
                (name == "Dodge_Back" and frame > 39) or 
                (name == "Dodge_Right" and frame > 39) or
                (name == "Dodge_ForwardLeft" and frame > 39) or 
                (name == "Dodge_ForwardRight" and frame > 39) or 
                (name == "Dodge_BackLeft" and frame > 39) or 
                (name == "Dodge_BackRight" and frame > 39)
            ):
                self.dodging = 0
#                self.head.influence = 1
                return
            
            if (
                (name == "Dodge" and frame > 29) or 
                (name == "Dodge_Left" and frame > 29) or 
                (name == "Dodge_Back" and frame > 29) or 
                (name == "Dodge_Right" and frame > 29) or
                (name == "Dodge_ForwardLeft" and frame > 29) or 
                (name == "Dodge_ForwardRight" and frame > 29) or 
                (name == "Dodge_BackLeft" and frame > 29) or 
                (name == "Dodge_BackRight" and frame > 29)
            ):
                dodgeMove = False
            
            actions = {
                1: ("Dodge", 1, 40, 0, 2, 1, 7),
                2: ("Dodge_Left", 1, 40, 0, 2, 1, 7),
                3: ("Dodge_Back", 1, 40, 0, 2, 1, 7),
                4: ("Dodge_Right", 1, 40, 0, 2, 1, 7),
                5: ("Dodge_ForwardLeft", 1, 40, 0, 2, 1, 7),
                6: ("Dodge_ForwardRight", 1, 40, 0, 2, 1, 7),
                7: ("Dodge_BackLeft", 1, 40, 0, 2, 1, 7),
                8: ("Dodge_BackRight", 1, 40, 0, 2, 1, 7)
            }
                
            if dodgeMove:
                self.moveProp = 0
                self.dodging = 1
                self.head.influence = 0
                self.anim.actionProp[1] = actions.get(self.dodgeVector[1])
                
                speed = 0.1
                vector = self.object.worldOrientation @ self.dodgeVector[0]
                vector.z = 0
                self.object.worldPosition = self.object.worldPosition + vector.normalized() * speed
    
    # End of Dodge Action
    # -------------------------------------------------------------
    # Start of Attack Action
    
#    def resetAttack(self):
#        if self.attackProp:
#            ft = bge.logic.getFrameTime() - self.attackFt
#            if ft >= 5:
##                self.actionState = self.state['Idle']
#                self.attackProp = 0

#            if self.actionState == self.state['Attack'] and self.action["Attack"] > self.actionProp[1][2]-2:
#                self.actionState = self.state['Guard']
#                self.actionProp[1] = 0
                
#    def startAttack(self):
#        if self.actionState == self.state['Down']:
#             return
#         
#        if not self.aim.active:
#            if self.attack.active and self.attack.activated:
#                if self.NearToEnemy.positive:
#                    target = self.NearToEnemy.hitObjectList[self.targetProp]
#                    dist, glo, loc = self.object.getVectTo(target)
#                    pos = target.worldPosition
#                    self.leapProp = (dist, glo, pos)
#                
#                if not self.leapProp:
#                    self.attackSeq()
#        else:
#            if self.attack.active:
#                if self.action['Charge'] > 1:
#                    self.chargeProp = 1
#                if self.action['Charge'] > 168:
#                    self.actionProp[1] = 0
#                    return
#                self.actionProp[1] = ('Charge', 1, 170, 0, 0, 1, 7)
#            else:
#                self.chargeAttack()

#    def startAttack(self):
#        if self.actionState == self.state['Down']:
#            return
#        
#        # For Gun
#        if self.aim.active and self.attack.active and self.attack.activated:
#            self.actionProp[3] = ("Shoot_Shotgun", 1, 34, 0, 1, 3, 0)
#            self.attacking = 1
#            self.attackFt = bge.logic.getFrameTime()
        
        # For Bow
#        if self.attack.active:
#            if not self.chargeProp:
#                self.attackProp = min(self.attackProp + 1, self.attackMx)
#                self.actionProp[3] = ("Shoot_Shotgun", 1, 37, 0, 1, 3, 7)
#                self.chargeProp = 1
#            elif not self.attacking:
#                self.actionProp[3] = ("Shoot_Shotgun", 27, 27, 1, 1, 3, 7)
#        else:
#            if self.chargeProp:
#                name, frame = self.getActionData(3) 
#                if name == "Shoot_Shotgun" and frame > 53:
#                    self.chargeProp = 0
#                    self.attacking = 0
#                    return
#                
#                self.actionProp[3] = ("Shoot_Shotgun", 27, 60, 0, 1, 3, 7)
#                self.attacking = 1
#                self.attackFt = bge.logic.getFrameTime()
                    
#    def chargeAttack(self):
#        if self.chargeProp:
#            frame = self.action['Charge']
#            if frame <= 50:
#                self.chargeProp = 1
#            elif frame <= 130:
#                self.chargeProp = 2
#            else:
#                self.chargeProp = 3
##            self.releaseAttack()
            
#    def releaseAttack(self):
#        self.chargeProp = 0
#        self.actionState = self.state['Charge']
            
#    def attackSeq(self):
#        # Enable to start next attack when last frame of attack are displayed
#        if self.attackProp:
#            if self.actionProp and 0 < self.action["Attack"] < self.actionProp[2]-2:
#                return
#        
#        # the number of sequence is along to weapon's attack value
#        if self.attackProp < len(self.atk):
#            self.attackProp += 1
#        else:
#            self.attackProp = 1
#        
#        # playAction Attack along to attackProp
#        frame = self.atk[self.attackProp-1]
#        self.actionProp = ("Attack", frame[0], frame[1], 0, 0, 1, 7)
#        self.attackFt = bge.logic.getFrameTime()
#        self.actionState = self.state['Attack']
        
#    def leapAttack(self):
#        if self.leapProp:  
#            dist, glo, pos = self.leapProp
#            vec = self.object.worldOrientation.col[1]
#            x = glo.x - vec.x
#            y = glo.y - vec.y
#            self.trackTo(glo, 0.3)
#            
#            if -0.1 < x < 0.1 and -0.1 < y < 0.1:
#                self.leapProp = 0
#                self.attackSeq()
#            
#            if dist > 4:
#                diff = self.object.worldPosition - pos
#                pos = self.object.worldPosition.copy()
#                pos = pos - diff / 20
#                self.object.worldPosition = pos
#                self.actionProp = ("Leap", 1, 60, 0, 0)
                
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
            
    def isDown(self):
        self.actionState = self.state['Down']
        self.torso.influence = 0
        self.head.influence = 0
        self.hand_L.influence = 0
        self.anim.actionProp[1] = ("Down", 1, 60, 0, 0, 1, 7)
        
    def resetHit(self):
        if self.actionState == self.state['Hit']:
            self.actionState = self.state['Idle']
    
    def isHit(self):
        self.actionState = self.state['Hit']
        self.torso.influence = 0
        self.head.influence = 0
        self.hand_L.influence = 0
        self.anim.actionProp[1] = ("Hit", 1, 13, 0, 0, 1, 7)

    # End of Attack Action
    # -------------------------------------------------------------
    # Start of Aim Action
                
#    def resetAim(self):
#        if self.aimProp and not self.cont.aim.active:
#            self.hud.showCrosshair(False)
#            self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 0, 0, 2, 7)
#            self.aimProp = 0
#            self.head.influence = 0
#            self.hand_L.influence = 0
#            self.torso.influence = 0
#            self.aimtimer = 0
                    
#    def startAim(self):
#        if self.cont.aim.active:
#            if not self.aimProp:
#                self.hud.showCrosshair()
#                self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 0, 0, 2, 7)
#                self.aimProp = 1
#            elif self.aimProp:
#                self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 1, 0, 2, 7)
#                self.rotateAim(self.cam.worldOrientation.col[0].to_3d())
#                if self.aimtimer <= 1:
#                    self.head.influence = self.aimtimer
#                    self.hand_L.influence = self.aimtimer
#                    self.torso.influence = 0.3
#                    self.aimtimer += 0.1
 
    # End of Aim Action
    # -------------------------------------------------------------
    # Start of Targeting Action
            
#    def resetTarget(self):
#        if not self.NearToEnemy.positive:
#            ft = bge.logic.getFrameTime() - self.targetFt
#            if self.targetProp and ft >= 3:
#                self.targetProp = 0
        
#    def detectTarget(self):
#        if self.NearToEnemy.positive:
#            
#            hitObjectList = self.NearToEnemy.hitObjectList
#            if self.targetProp >= len(hitObjectList):
#                self.targetProp = len(hitObjectList)-1
#             
#            self.targetFt = bge.logic.getFrameTime()
#            object = hitObjectList[self.targetProp]
#            if object.children:
#                sphere = object.children[1]
#                target = sphere.children[0]
#                
#                vec = sphere.getVectTo('Camera')
#                sphere.alignAxisToVect((0, 0, 1), 2)
#                sphere.alignAxisToVect(vec[1], 1)

    # End of Targeting Action
    # -------------------------------------------------------------
    # Start of Interact Action
    
    def startInteract(self):
        self.detectInteract()
        
        if self.interProp and self.cont.interact.active and self.cont.interact.activated:
            offset = Vector([0,0,1])
            self.snapProp = (self.interProp, offset, 0)
    
    def detectInteract(self):
        bottom = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0,-1]))
        rotation = Matrix.Rotation(radians(90), 4, 'Z')
        cam_forward = rotation @ self.camLook.worldOrientation.col[0]
        target = bottom + (cam_forward * 3)
        bge.render.drawLine(target, bottom, [0,1,1])
        objB, hitB, normB = self.object.rayCast(target, bottom, face=1, xray=1, mask=0x0001)
        
        if hitB:
            tmp = hitB + (normB * Vector([0.4,0.4,0]))
            bge.render.drawLine(hitB, tmp, [1,1,0])
            self.interProp = (objB, tmp, normB)
        else:
            self.interProp = 0
    
    # End of Interact Action