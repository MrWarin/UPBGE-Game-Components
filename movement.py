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
        ("Dodge ON/OFF", True),
        ("Debug ON/OFF", True)
    ])

    def start(self, args):
        self.movOnOff = args['Movement ON/OFF']
        self.walkSpeed = args['Walk Speed']
        self.runSpeed = args['Run Speed']
        self.croOnOff = args['Crouch ON/OFF']
        self.jumOnOff = args['Jump ON/OFF']
        self.cliOnOff = args['Climb ON/OFF']
        self.dodOnOff = args['Dodge ON/OFF']
        self.debug = args['Debug ON/OFF']
        
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
        self.footplace = self.object.components['footplace']
        self.lookat = self.camLook.components['camera']

        # Constraint
        self.character = bge.constraints.getCharacter(self.object)
        self.hand_R = bpy.data.objects["Armature"].pose.bones["Hand.IK.R"].constraints["Copy Location"]
        self.hand_L = bpy.data.objects["Armature"].pose.bones["Hand.IK.L"].constraints["Copy Location"]
#        self.head = bpy.data.objects["Armature"].pose.bones["Neck"].constraints["Track To"]
#        self.hand_L = bpy.data.objects["Armature"].pose.bones["Hand.IK.L"].constraints["Copy Location"]
        
        # Movement Prop
        self.moveProp = 1
        self.runProp = 0
        self.leapProp = 0
        self.dodgeProp = 0
        self.dodging = 0
        self.dodgeVector = 0
        self.jumpFt = 0
        self.stateTmp = 0
        self.speed = 0

        # Climb Prop
        self.climbStep = 0
        self.climbProp = 0
#        self.snapProp = 0
#        self.wallProp = 0
#        self.topProp = 0
#        self.bottomProp = 0
#        self.floorProp = 0
#        self.edgeProp = 0
#        self.headProp = 0
#        self.edgeFt = 0
#        self.tmpProp = 0
#        self.midProp = 0
        self.edge = 0
        self.climbFinish = False
        self.readyToClimb = True
        self.climbLength = 1
        self.climbHeight = 2
        self.climbDirection = False
        self.climbOffset = 0
        self.branchObj = 0
        self.last_move_direction = 0
        
        # Attack Prop
#        self.chargeProp = 0
#        self.attackProp = 0
#        self.aimProp = 0
#        self.attackFt = 0
#        self.attackMx = 3
#        self.targetProp = 0
#        self.targetFt = 0
#        self.targetPos = (0, 0)
#        self.guardFt = 0
#        self.attacking = 0
        
        # Anim Prop
        self.actionState = 0
        self.ragdoll = True
        self.interProp = 0
        self.width = 0.55
        self.height = 1.4
        
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
        
        self.handEnable()

    def update(self):
        self.Idle()
        self.startInteract()
        
        if self.movOnOff == True:
            self.resetRun()
            self.startRun()
            
        if self.cliOnOff == True:
            self.resetClimb()
            self.startClimb()
            
        if self.jumOnOff == True:
            self.resetJump()
            self.startJump()
        
#        if self.croOnOff == True:
#            self.resetCrouch()
#            self.startCrouch()
            
        if self.dodOnOff == True:
            self.resetDodge()
            self.startDodge()
            
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
#        print(list(self.state.keys())[self.actionState], self.anim.actionProp)
        
    # -------------------------------------------------------------
    # Start of Idle Action
        
    def Idle(self):
        if self.actionState == self.state['Idle']:
            self.anim.actionProp[1] = ("Idle", 0, 72, 1, 99, 7)
        
#        elif self.actionState == self.state['Crouch']:
#            self.anim.actionProp[1] = ("Crouch", 30, 90, 1, 99, 1, 7)
            
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
                self.anim.actionProp[1] = ("Crouch", 30, 1, 0, 1, 7)
              
    def startCrouch(self):
        if self.actionState == self.state['Idle']:
            if not self.climbProp and self.cont.crouch.active:
                self.actionState = self.state['Crouch']
                self.anim.actionProp[1] = ("Crouch", 1, 30, 0, 1, 7)
            
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
                self.anim.actionProp[1] = (action, 1, 56, 0, priority, 7)
                
            # Reset sneak state
#            if self.actionState == self.state['Sneak']:
#                self.actionState = self.state['Crouch']
#                action = "RunToIdle_R" if name == "Sneak" and (30 <= frame <= 60 or 15 <= frame <= 28) else "RunToIdle_L"
#                self.anim.actionProp[1] = (action, 1, 56, 0, 2, 7)
                    
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
        
        if self.character.onGround and not self.cont.aim.active and self.cont.sprint.active and self.cont.sprint.activated:
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
                    1: ("Walk", 17, 68, 1, 2, 7),
                    2: ("Walk_Left", 17, 68, 1, 2, 7),
                    3: ("Walk_Back", 17, 68, 1, 2, 7),
                    4: ("Walk_Right", 17, 68, 1, 2, 7),
                    5: ("Walk_ForwardLeft", 17, 68, 1, 2, 7),
                    6: ("Walk_ForwardRight", 17, 68, 1, 2, 7),
                    7: ("Walk_BackLeft", 17, 68, 1, 2, 7),
                    8: ("Walk_BackRight", 17, 68, 1, 2, 7)
                }
            
            self.anim.actionProp[1] = actions.get(self.runProp)
            
        # Run State
        if self.actionState in [self.state['Run']]:
            if self.cont.aim.active:
                self.actionState = self.state['Idle']
            
            self.stateTmp = self.actionState
            priority = 1 if name == "Jump" and frame > 59 else 2
            actions = ("Run", 1, 52, 0, priority, 7)
            if (name == "Run" and frame > 49):
                actions = ("Run", 52, 102, 1, 2, 7)
            
            self.anim.actionProp[1] = actions
                
        # Sneak State
#        if self.actionState in [self.state['Crouch'], self.state['Sneak']]:
#            self.actionState = self.state['Sneak']
#            self.stateTmp = self.actionState
#            actions = {
#                1: ("Sneak", 1, 30, 0, 1, 1, 7),
#                2: ("Sneak_Left", 1, 20, 0, 1, 1, 7),
#                3: ("Sneak_Back", 1, 12, 0, 1, 1, 7),
#                4: ("Sneak_Right", 1, 20, 0, 1, 1, 7),
#                5: ("Sneak_ForwardLeft", 1, 21, 0, 1, 1, 7),
#                6: ("Sneak_ForwardRight", 1, 21, 0, 1, 1, 7),
#                7: ("Sneak_BackLeft", 1, 20, 0, 1, 1, 7),
#                8: ("Sneak_BackRight", 1, 20, 0, 1, 1, 7)
#            }
#            
#            if (
#                self.action["Sneak"] > 49 or 
#                self.action["Sneak_Left"] > 18 or 
#                self.action["Sneak_Back"] > 9 or 
#                self.action["Sneak_Right"] > 18 or 
#                self.action["Sneak_ForwardLeft"] > 18 or 
#                self.action["Sneak_ForwardRight"] > 18 or 
#                self.action["Sneak_BackLeft"] > 17 or 
#                self.action["Sneak_BackRight"] > 17
#            ):
#                actions = {
#                    1: ("Sneak", 52, 102, 1, 2, 1, 7),
#                    2: ("Sneak_Left", 21, 70, 1, 2, 1, 7),
#                    3: ("Sneak_Back", 12, 56, 1, 2, 1, 7),
#                    4: ("Sneak_Right", 21, 70, 1, 2, 1, 7),
#                    5: ("Sneak_ForwardLeft", 21, 70, 1, 2, 1, 7),
#                    6: ("Sneak_ForwardRight", 21, 70, 1, 2, 1, 7),
#                    7: ("Sneak_BackLeft", 20, 65, 1, 2, 1, 7),
#                    8: ("Sneak_BackRight", 20, 65, 1, 2, 1, 7)
#                }
        
#        if actions:
#            self.anim.actionProp[1] = actions.get(self.runProp)
        
        # Turn and move
        if self.stateTmp == self.state['Run']:
            speed = self.runSpeed
            rot = self.camLook.worldOrientation @ self.camLook.worldOrientation.Rotation(radians, 3, 'Z')
            self.edge = 0
        else:
            speed = self.walkSpeed
            rot = self.camLook.worldOrientation
            self.edge = radians
            
        loc = self.camLook.worldOrientation @ vector
#        loc_vec = self.object.worldOrientation @ loc_vec
        loc.z = 0
        self.speed = (speed * self.cont.dt)
        self.object.worldPosition = self.object.worldPosition + loc.normalized() * self.speed
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
#            self.jumpFt += 1*self.dt
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
#            self.jumpFt += 1 * self.dt
            
            if self.character.onGround:
                self.footplace.enable()
                if self.runProp:
                    self.anim.actionProp[1] = ("Leap", 60, 119, 0, 1, 7)
                    self.actionState = self.stateTmp
                else:
                    self.anim.actionProp[1] = ("Jump", 60, 119, 0, 1, 7)
                    self.actionState = self.state['Idle']
                
#                if self.jumpFt > 1:
#                    damage = ceil(100 * self.jumpFt)
#                    print(f"Fall Damage: {damage}")
#                    self.isAttacked(damage)
                    
#                self.jumpFt = 0
            else:
                name, frame = self.anim.getActionData(1)
                if (name == "Jump" and frame > 59) or (name == "Leap" and frame > 59):
                    self.anim.actionProp[1] = ("Jump", 58, 58, 1, 2, 7)

    def startJump(self):
        if self.actionState in [self.state['Idle'], self.state['Run'], self.state['Walk'], self.state['Jump']]:
            if self.cont.jump.active and self.cont.jump.activated:
                
                if self.readyToClimb and self.climbProp:
                    self.actionState = self.state['Climb']
                    return
                
                if self.character.onGround:
                    self.anim.actionProp[1] = ("Jump" if self.actionState == self.state['Idle'] else "Leap", 1, 60, 0, 1, 1, 7)
                elif self.character.jumpCount < self.character.maxJumps:
                    self.anim.actionProp[1] = ("Leap", 1, 60, 0, 1, 7)
                    
                self.character.jump()
                self.footplace.disable()
                self.stateTmp = self.actionState
                self.actionState = self.state['Jump']

    # End of Jump Action
    # -------------------------------------------------------------
    # Start of Climb Action
    
    def resetClimb(self):
#        if not self.readyToClimb and self.actionState == self.state['Climb']:
        if self.climbFinish and self.actionState == self.state['Climb']:
            
            if self.detectFloor():
                stat = "Idle" if self.climbStep == 2 else "Jump"
                self.actionState = self.state[stat]
                self.readyToClimb = True
                self.climbFinish = False
            
            self.climbProp = 0
            self.moveProp = 1
            self.climbStep = 0
            self.climbLength = 1
            self.climbHeight = 2
            
            self.arm.playAction('Idle', 1, 1)
            new_matrix = self.object.worldOrientation @ Matrix.Rotation(radians(180), 3, 'Z')
            new_matrix = self.arm.worldOrientation.lerp(new_matrix, 1)
            self.arm.worldPosition = self.object.worldPosition + Vector([0,0,-1.37])
            self.arm.worldOrientation = new_matrix
            
            self.arm.setParent(self.object)
            self.footplace.enable()
            self.lookat.enable()
            self.handEnable()
            self.object.restorePhysics()
            
#        if not self.readyToClimb and self.climbFinish and self.detectFloor():
#            self.actionState = self.state['Jump']
#            self.readyToClimb = True
#            self.climbFinish = False

    def startClimb(self):
        if self.readyToClimb:
            self.detectLedge()
            self.detectEdge()
            self.detectLadder()
            self.detectBranch()
            # self.detectCorner()
            # self.detectFloor()

        if self.readyToClimb and self.climbProp and not self.character.onGround:
            self.actionState = self.state['Climb']

        if self.actionState == self.state['Climb']:
            name, frame = self.anim.getActionData(1)
            action = False
            move_direction = Vector([0, 0, 0])
            
            if self.climbStep == 1:
                if self.detectFloor():
                    self.readyToClimb = False
                    self.climbFinish = True
                    self.character.reset()
                
                blend = 7
                start = 1
                self.climbLength = 0.55
                self.climbHeight = 2
                
                if not self.arm.parent:
                    blend = 0
                    start = 60
                    self.arm.playAction('Climb', 61, 61)
                    new_matrix = self.object.worldOrientation @ Matrix.Rotation(radians(180), 3, 'Z')
                    new_matrix = self.arm.worldOrientation.lerp(new_matrix, 1)
                    self.arm.worldPosition = self.object.worldPosition + Vector([0,0,-1.37])
                    self.arm.worldOrientation = new_matrix
                    self.arm.setParent(self.object)
                
                self.climbOffset = 0
                move_action = ""
                    
                action = ("Climb", start, 60, 0, 1, blend)
                if (name == "Climb" and frame > 59):
                    action = ("Climb", 61, 140, 1, 1, 7)
                
                if self.cont.forward.active and self.cont.forward.activated:
                    self.climbStep = 2
                elif self.cont.back.active and self.cont.back.activated:
                    self.readyToClimb = False
                    self.climbFinish = True
                elif self.cont.right.active:
                    self.climbOffset = 0.55
                    move_direction += self.object.worldOrientation.col[0]
                    self.climbDirection = "right"
                elif self.cont.left.active:
                    self.climbOffset = -0.55
                    move_direction -= self.object.worldOrientation.col[0]
                    self.climbDirection = "left"
                    
                edge = self.isLedgeEnd(self.climbOffset, move_direction)
                if edge == True:
                    self.object.worldPosition += move_direction.normalized() * (1 * self.cont.dt)
                    action = (f"Climb_{self.climbDirection}", 1, 60, 1, 1, 7)
                elif edge == "Outer":
                    action = (f"Climb_outer_{self.climbDirection}", 1, 40, 0, 1, 7)
                    if (name == f"Climb_outer_{self.climbDirection}" and frame > 39):
#                        self.climbStep = 3
                        if self.isLedgeCorner(self.climbOffset): 
                            return
                elif edge == "Inner":
                    action = (f"Climb_inner_{self.climbDirection}", 1, 20, 0, 1, 7)
                    if (name == f"Climb_inner_{self.climbDirection}" and frame > 19):
#                        self.climbStep = 4
                        if self.isLedgeCorner(self.climbOffset):
                            return
            
            elif self.climbStep == 2:
                self.arm.removeParent()
                self.character.reset()
                action = ("Climb_up", 1, 124, 0, 1, 7)
                if (name == "Climb_up" and frame > 123):
                    self.readyToClimb = False
                    self.climbFinish = True
                    
            elif self.climbStep == 3:
                self.arm.removeParent()
                action = (f"Climb_outer_{self.climbDirection}", 41, 100, 0, 1, 0)
                if (name == f"Climb_outer_{self.climbDirection}" and frame > 99):
                    self.climbStep = 1
#                    if self.isLedgeCorner(self.climbOffset):
#                        return
                    
            elif self.climbStep == 4:
                self.arm.removeParent()
                action = (f"Climb_inner_{self.climbDirection}", 21, 40, 0, 1, 0)
                if (name == f"Climb_inner_{self.climbDirection}" and frame > 39):
                    self.climbStep = 1
#                    if self.isLedgeCorner(self.climbOffset):
#                        return
            
            elif self.climbStep == 5:
                if self.cont.jump.active and self.cont.jump.activated:
                    self.readyToClimb = False
                    self.climbFinish = True
                    
                self.character.reset()
                start = 1
                if self.climbDirection:
                    start = 45
                    
                self.climbDirection = ""
                action = ("Climb_ladder", start, 45, 0, 1, 7)
                if (name == "Climb_ladder" and frame > 44):
                    action = ("Climb_ladder", 45, 120, 1, 1, 7)
                
                if self.cont.forward.active:
                    move_direction += self.object.worldOrientation.col[2]
                    self.climbDirection = "up"
                elif self.cont.back.active:
                    move_direction -= self.object.worldOrientation.col[2]
                    self.climbDirection = "down"
                    if self.detectFloor():
                        self.readyToClimb = False
                        self.climbFinish = True
                    
                self.object.worldPosition += move_direction.normalized() * (1.5 * self.cont.dt)
                if self.climbDirection == "up":
                    action = (f"Climb_ladder_{self.climbDirection}", 1, 60, 1, 1, 7)
                elif self.climbDirection == "down":
                    action = (f"Climb_ladder_{self.climbDirection}", 1, 60, 1, 1, 7)
                    
            elif self.climbStep == 6:
                if not self.climbProp:
                    self.readyToClimb = False
                    self.climbFinish = True
                
                # Retrieve the necessary vectors from the objects
                if self.climbProp:
                    obj_y_axis = self.climbProp[0].worldOrientation.col[1]  # Y-axis of the object
                    cam_x_axis = self.camLook.worldOrientation.col[0]       # X-axis of the camera
                    cam_z_axis = self.camLook.worldOrientation.col[2]       # Z-axis of the camera

                    # Calculate the dot products
    #                combined_direction = (obj_y_axis * cam_z_axis).normalized()
                    dot_x = obj_y_axis.dot(cam_x_axis)
                    dot_z = obj_y_axis.dot(cam_z_axis)
                    threshold = 0.1

                    # Get the reference position along the Y-axis of the target object
                    target_position = self.climbProp[0].worldPosition
    #                reference_y_pos = target_position.y

                    # Determine movement direction based on control and camera orientation
                    if self.cont.forward.active:
                        move_direction = obj_y_axis if dot_z >= threshold else -obj_y_axis
                    elif self.cont.back.active:
                        move_direction = -obj_y_axis if dot_z >= threshold else obj_y_axis
                    elif self.cont.right.active:
                        move_direction = obj_y_axis if dot_x >= threshold else -obj_y_axis
                    elif self.cont.left.active:
                        move_direction = -obj_y_axis if dot_x >= threshold else obj_y_axis

                    # Calculate the new position and move the character
                    if move_direction.length > 0.01:
                        self.last_move_direction = move_direction
                        new_position = self.object.worldPosition + move_direction.normalized() * self.speed
                        new_position = target_position + obj_y_axis.dot(new_position - target_position) * obj_y_axis
                        self.object.worldPosition = new_position
                    
                    # Calculate the target orientation
                    if self.last_move_direction.length > 0.01:
                        target_orientation = self.last_move_direction.to_track_quat('Y', 'Z').to_matrix().to_3x3()
                        current_orientation = self.object.worldOrientation
                        self.object.worldOrientation = current_orientation.lerp(target_orientation, 0.1)
                
            if self.climbProp:
                if self.climbStep in [0, 2, 5, 6]:
                    if self.climbStep == 0:
                        self.climbStep = 1
                        
                    self.moveProp = 0
                    self.object.suspendPhysics(1)
                    self.footplace.disable()
                    self.lookat.disable()
                    self.handDisable()

                # Project the object's position onto the plane
                climb_position = self.climbProp[1]
                normal_vector = self.climbProp[2]
                object_to_climb = self.object.worldPosition - climb_position
                projection = object_to_climb - normal_vector * object_to_climb.dot(normal_vector)
                new_position = climb_position + projection
                
                if self.climbStep in [1, 2]:
                    new_position.z = climb_position.z
                elif self.climbStep == 5:
                    new_position.xy = climb_position.xy
                elif self.climbStep == 6:
                    new_position.z = climb_position.z

                # Lock object to climbProp's normal vector
                self.object.alignAxisToVect(normal_vector, 1, 0.1)
                self.object.alignAxisToVect([0, 0, 1], 2, 1)
                self.object.worldPosition = new_position
                
                if action:
                    self.anim.actionProp[1] = action
            
    def detectLedge(self):
        top = self.object.worldPosition + (self.object.worldOrientation @ Vector([0, self.climbLength, self.climbHeight]))
        target = top - Vector([0, 0, self.climbHeight])
        _, hitT, normT = self.object.rayCast(target, top, face=1, xray=1, prop='scene', mask=0x0001)
        if self.debug:
            bge.render.drawLine(top, target, [0, 0, 1])
        
        if hitT:
            head = self.object.worldPosition.copy()
            head.z = hitT.z - 0.1
            target = head - self.object.worldOrientation @ Vector([0, -1, 0])
            _, hitH, normH = self.object.rayCast(target, head, xray=1, face=1, prop='scene', mask=0x0001)
            if self.debug:
                bge.render.drawLine(target, head, [0, 0, 1])

            if hitH:
                if self.climbStep == 1 and self.detectFloor() and self.character.onGround:
                    self.climbStep = 2

                tmp = Vector([hitH.x, hitH.y, hitT.z])
                if self.climbStep in [0, 1, 3, 4]:
                    tmp.z -= 1.37
                    tmp += Vector([-normH.x * -0.2, -normH.y * -0.2, 0])
                
                elif self.climbStep == 2:
                    tmp.z += 1.37
                    tmp += Vector([-normH.x * 0.55, -normH.y * 0.55, 0])

                self.climbProp = (_, tmp, -normH)
            else:
                self.climbProp = 0
        else:
            self.climbProp = 0
            
    def detectLadder(self):
        if self.climbStep in [0, 5]:
            front = self.object.worldPosition + Vector([0, 0, 1.37])
            target = front - (self.object.worldOrientation @ Vector([0, -1, 0]))
            bge.render.drawLine(target, front, [0,0,1])
            obj, _, norm = self.object.rayCast(target, front, xray=1, face=0, prop='ladder', mask=0x0001)
            
            if self.climbStep == 0 and obj and ((self.cont.jump.active and self.cont.jump.activated) or self.character.onGround == False):
                self.climbStep = 5
            
            if self.climbStep == 5:
                if obj:
                    tmp = Vector([obj.worldPosition.x, obj.worldPosition.y, self.object.worldPosition.z])
                    tmp.xy += Vector([-norm.x * -0.2, -norm.y * -0.2])
                    self.climbProp = (_, tmp, -norm)
                else:
                    self.climbStep = 2
                    self.climbProp = 0
                    
    def detectBranch(self):
        if self.climbStep in [0, 6]:
            front = self.object.worldPosition + (self.object.worldOrientation @ Vector([0, 0, 0]))
            target = front - Vector([0, 0, 1.38])
            bge.render.drawLine(target, front, [0,0,1])
            obj, _, _ = self.object.rayCast(target, front, xray=1, face=1, prop='branch', mask=0x0001)
            
            if obj:
                if self.climbStep == 0:
                    self.climbStep = 6
            else:
                self.climbStep = 0
                
            if self.climbStep == 6:
                if obj and not self.detectFloor():
                    tmp = Vector([self.object.worldPosition.x, self.object.worldPosition.y, obj.worldPosition.z])
                    tmp.z += 1.37
                    self.climbProp = (obj, tmp, _)
                    self.actionState = self.state['Climb']
                else:
                    self.climbProp = 0
        
    def detectEdge(self):
        if self.runProp and not self.climbProp and self.climbStep == 0:
            legnth = 0.4
            rot = self.object.worldOrientation @ Vector([0,legnth,0])
            rot = rot @ Matrix.Rotation(-self.edge, 3, 'Z')
            bottom = self.object.worldPosition + (rot)
            target = bottom - Vector([0,0,4])
            _, hitB, normB = self.object.rayCast(target, bottom, xray=1, face=1, prop='scene', mask=0x0001)
            if self.debug:
                bge.render.drawLine(bottom, target, [1,0,0])
            
            if hitB:
                self.readyToClimb = True
            
            if not hitB:
                rot = self.object.worldOrientation @ Vector([0,legnth,-1.5])
                rot = rot @ Matrix.Rotation(-self.edge, 3, 'Z')
                rear = self.object.worldPosition + (rot)
                
                rot = self.object.worldOrientation @ Vector([0,legnth,0])
                rot = rot @ Matrix.Rotation(-self.edge, 3, 'Z')
                target = rear - rot
                
                _, hitR, normR = self.object.rayCast(rear, target, xray=1, face=1, prop='scene', mask=0x0001)
                if self.debug:
                    bge.render.drawLine(rear, target, [1,0,0])
        
                if hitR:
                    # To prevent falling from edge
                    rot = self.object.worldOrientation @ Vector([0,-legnth,0])
                    rot = rot @ Matrix.Rotation(-self.edge, 3, 'Z')
                    pos = hitR + rot
                    pos = self.object.worldPosition.lerp([pos.x, pos.y, self.object.worldPosition.z], 0.5)
                    self.object.worldPosition = pos

    def isLedgeEnd(self, offset, move_direction):
        if offset:
            top = self.object.worldPosition + (self.object.worldOrientation @ Vector([offset, self.climbLength, 2]))
            target = top - Vector([0, 0, 2])
            _, hitT, _ = self.object.rayCast(target, top, face=1, prop='scene', mask=0x0001)
            if self.debug:
                bge.render.drawLine(top, target, [0, 0, 1])
                
            if hitT:
                return True
            else:
                corner = self.check_corner(offset)
                return corner[0]

        return False
                
    def isLedgeCorner(self, offset):
#        offset = offset * 1.1
#        corner = [
#            ([offset, self.climbLength, 1.27], [offset, 0, 0], 3, "Outer"), # Outer
#            ([0, -0.4, 1.27], [-offset, 0, 0], 4, "Inner") # Inner
#        ]
#        
#        for x in corner:
#            hit, norm = self.check_ledge(x[0], x[1])
##            if hit and self.cont.jump.active and self.cont.jump.activated:
#            if hit:
#                hit.z -= 1.37
#                hit += Vector([-norm.x * -0.2, -norm.y * -0.2, 0])
#                climb_position = hit
#                normal_vector = -norm
#                
#                self.climbStep = x[2]
#                self.arm.removeParent()
##                self.climbProp = (climb_position, normal_vector)
#                self.object.alignAxisToVect(normal_vector, 1, 1)
#                self.object.alignAxisToVect([0, 0, 1], 2, 1)
#                self.object.worldPosition = climb_position
#                return x[3]
        corner, position, climbStep = self.check_corner(offset)
        if corner:
            self.climbStep = climbStep
#            self.climbStep = 1
            self.arm.removeParent()
            self.object.alignAxisToVect(position[1], 1, 1)
            self.object.alignAxisToVect([0, 0, 1], 2, 1)
            self.object.worldPosition = position[0]
            return corner

        return False
    
    def check_ledge(self, start, end):
        top = self.object.worldPosition + (self.object.worldOrientation @ Vector(start))
        target = top - (self.object.worldOrientation @ Vector(end))
        _, hit, norm = self.object.rayCast(target, top, face=1, xray=1, prop='scene', mask=0x0001)
        bge.render.drawLine(top, target, [0, 1, 1])
        return hit, norm
    
    def check_corner(self, offset):
        offset = offset * 1.1
        corners = {
            "Outer": ([offset, 0.75, 1.27], [offset, 0, 0], 3),
            "Inner": ([0, -0.4, 1.27], [-offset, 0, 0], 4)
        }
        
        for corner in corners.items():
            hit, norm = self.check_ledge(corner[1][0], corner[1][1])
            if hit:
                hit.z -= 1.27
                hit += Vector([-norm.x * -0.2, -norm.y * -0.2, 0])
                return (corner[0], (hit, -norm), corner[1][2])

        return (False, False, False)
            
    def detectFloor(self):
        below = self.object.worldPosition + Vector([0,0,-1.4])
        bge.render.drawLine(self.object.worldPosition, below, [0,0,1])
        _, hit, _ = self.object.rayCast(below, None, xray=1, face=1, prop='scene', mask=0x0001)
        
        if hit:
            return True
        
        return False
        
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
#            self.anim.actionProp[1] = (anim, start, end, 0, 0)
        
        if not hit or not norm:
            self.climbProp = 0
            self.snapProp = 0
            return
        
        if norm:
            diff = self.object.worldOrientation.col[1]
            dot = diff.dot(-norm)
            threshold = 0.9997
#           print(diff, dot, threshold)
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
                1: ("Dodge", 1, 40, 0, 2, 7),
                2: ("Dodge_Left", 1, 40, 0, 2, 7),
                3: ("Dodge_Back", 1, 40, 0, 2, 7),
                4: ("Dodge_Right", 1, 40, 0, 2, 7),
                5: ("Dodge_ForwardLeft", 1, 40, 0, 2, 7),
                6: ("Dodge_ForwardRight", 1, 40, 0, 2, 7),
                7: ("Dodge_BackLeft", 1, 40, 0, 2, 7),
                8: ("Dodge_BackRight", 1, 40, 0, 2, 7)
            }
                
            if dodgeMove:
                self.moveProp = 0
                self.dodging = 1
#                self.head.influence = 0
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
            
    def isDown(self):
        self.actionState = self.state['Down']
        self.torso.influence = 0
        self.head.influence = 0
        self.hand_L.influence = 0
        self.anim.actionProp[1] = ("Down", 1, 60, 0, 0, 7)
        
    def resetHit(self):
        if self.actionState == self.state['Hit']:
            self.actionState = self.state['Idle']
    
    def isHit(self):
        self.actionState = self.state['Hit']
        self.torso.influence = 0
        self.head.influence = 0
        self.hand_L.influence = 0
        self.anim.actionProp[1] = ("Hit", 1, 13, 0, 0, 7)

    # End of Attack Action
    # -------------------------------------------------------------
    # Start of Aim Action
                
#    def resetAim(self):
#        if self.aimProp and not self.cont.aim.active:
#            self.hud.showCrosshair(False)
#            self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 0, 0, 7)
#            self.aimProp = 0
#            self.head.influence = 0
#            self.hand_L.influence = 0
#            self.torso.influence = 0
#            self.aimtimer = 0
                    
#    def startAim(self):
#        if self.cont.aim.active:
#            if not self.aimProp:
#                self.hud.showCrosshair()
#                self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 0, 0, 7)
#                self.aimProp = 1
#            elif self.aimProp:
#                self.anim.actionProp[2] = ("Shoot_Shotgun", 1, 1, 1, 0, 7)
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
            type = self.interProp[0]['hud']
            ammo = self.interProp[0]['ammo']
            self.interProp[0]['ammo'] -= self.shoot.getAmmo(type, ammo)
#            offset = Vector([0,0,1])
#            self.snapProp = (self.interProp, offset, 0)
    
    def detectInteract(self):
        bottom = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0,-1]))
        rotation = Matrix.Rotation(radians(90), 4, 'Z')
        cam_forward = rotation @ self.camLook.worldOrientation.col[0]
        target = bottom + (cam_forward * 3)
        objB, hitB, normB = self.object.rayCast(target, bottom, face=1, xray=1, mask=0x0001)
        if self.debug:
            bge.render.drawLine(target, bottom, [0,1,1])
        
        if hitB:
            tmp = hitB + (normB * Vector([0.4,0.4,0]))
            self.interProp = (objB, tmp, normB)
            if self.debug:
                bge.render.drawLine(hitB, tmp, [1,1,0])
        else:
            self.interProp = 0
            
    def handEnable(self):
        self.hand_R.influence = 1
        self.hand_L.influence = 1
        
    def handDisable(self):
        self.hand_R.influence = 0
        self.hand_L.influence = 0
    
    # End of Interact Action