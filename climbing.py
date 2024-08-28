import bge
from math import sqrt
from mathutils import Vector
from collections import OrderedDict

class climbing(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ("Climbing ON/OFF", True)
    ])

    def start(self, args):
        self.enable = args['Climbing ON/OFF']
        self.point1 = self.object
        self.point2 = self.object.scene.objects["Point2"]
        self.point3 = self.object.scene.objects["Point3"]
        self.vertex_count = 8

    def update(self):
        if self.enable:
            self.resetClimb()
            self.startClimb()
    
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
#                self.object.suspendPhysics(1)
                self.anim.actionProp[1] = ("IdleToClimb", 60, 60, 0, 0, 7, 1, 7)
                self.midProp = 0
                self.tmpProp = 0
            
            if self.climbProp == 2 and self.cont.forward.active and self.cont.forward.activated:
                # Check if character is hanging on the top of building
                _, hit, norm = self.topProp
                diff = hit.z - (self.object.worldPosition.z + 1.45)
                if diff > 0.001:
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
                    if diff.z > 0.001:
    #                    inter = self.object.worldPosition.lerp(hit - Vector([0,0,-1.42]), 0.8*self.deltatime)
    #                    self.object.worldPosition.z = inter.z
                        
                        self.object.worldPosition.z += 2*self.deltatime
                    else:
                        if not self.tmpProp:
                            self.tmpProp = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.75,0]))
                            
                        diff = self.object.worldPosition - self.tmpProp
                        if self.tmpProp and diff.length > 0.05:
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
                        if mid.z > 0.001:
                            self.object.worldPosition.z += 3*self.deltatime
                        else:
                            self.midProp = 1
                            self.tmpProp = 0
                            self.climbProp = 3
                        return
                    
                    diff = hit - (self.object.worldPosition + Vector([0,0,1.45]))
                    if diff.z > 0.001:
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
            self.footplace_Root.influence = 0
            self.footplace_R.influence = 0
            self.footplace_L.influence = 0
            self.object.suspendPhysics(1)
            
            self.anim.actionProp[1] = ("IdleToClimb_Down", 1, 120, 0, 0, 1, 7)
                
#            if self.action['IdleToClimb_Down'] >= 100:
            name, frame = self.anim.getActionData(1)
            if name == "IdleToClimb_Down" and frame > 100:
#                hit = self.topProp[1] if self.topProp else 0
                
                edge = self.edgeProp if self.edgeProp else 0
                
                self.object.worldPosition = edge[0]
                self.object.alignAxisToVect(-edge[1], 1, 1)
                self.object.alignAxisToVect((0, 0, 1), 2, 1)
                
                vec = self.object.worldPosition
                self.arm.worldPosition = Vector([vec[0], vec[1], vec[2] - 1.42])
                self.arm.alignAxisToVect(edge[1], 1, 1)
                self.arm.alignAxisToVect((0, 0, 1), 2, 1)
                self.arm.setParent(self.object)
                
                self.footplace_Root.influence = 1
                self.footplace_R.influence = 1
                self.footplace_L.influence = 1
#                
                self.anim.actionProp[1] = ("IdleToClimb", 60, 60, 0, 0, 1, 0)
                self.climbProp = 2
                
#            if self.action['IdleToClimb_Down'] > 17:
            if name == "IdleToClimb_Down" and frame > 17:
                edge = self.edgeProp if self.edgeProp else 0
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
                        
                    destination = Vector(edge[0])
                    diff = destination - self.object.worldPosition
                    if diff.length > 0.05:
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
                
                if diff.z < -0.001:
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
        _, hitT, normT = self.object.rayCast(target, top, face=1, xray=1, prop='scene')
        
        if hitT:
            self.topProp = (_, hitT, normT)
        else:
            self.topProp = 0
            
        bottom = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,length,1.4]))
        target = bottom - Vector([0,0,5])
        bge.render.drawLine(bottom, target, [0,0,1])
        _, hitB, normB = self.object.rayCast(target, bottom, face=1, prop='scene')
        
        if hitB:
            self.bottomProp = (_, hitB, normB)
        else:
            self.bottomProp = 0
        
        front = self.object.worldPosition + (self.object.worldOrientation.col[1])
        bge.render.drawLine(self.object.worldPosition, front, [0,0,1])
        _, hitW, normW = self.object.rayCast(front, None, face=1, prop='scene')
        
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
        _, hitH, normH = self.object.rayCast(target, head, face=1, prop='scene')
        
        if hitH:
            self.headProp = (_, hitH, normH)
        else:
            self.headProp = 0
        
    def detectEdge(self):
        if not self.climbProp and self.moveProp:
            if not self.runProp:
                self.edgeFt = 0
                
            mid = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.35,0]))
            target = mid - Vector([0,0,1.42])
            bge.render.drawLine(mid, target, [0,0,1])
            _, hitM, normM = self.object.rayCast(target, mid, face=1, prop='scene')
            
            rear = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.35,-1.42]))
            target = rear - self.object.worldOrientation @ Vector([0,0.5,0])
            bge.render.drawLine(rear, target, [0,0,1])
            _, hitR, normR = self.object.rayCast(rear, target, face=1, prop='scene')
        
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
        start = self.object.worldPosition + (self.object.worldOrientation @ Vector([0,0.45,0]))
        
        right = start - self.object.worldOrientation @ Vector([-0.3,0,0])
        bge.render.drawLine(start, right, [1,0,0])
        _, hitR, normR = self.object.rayCast(right, start, face=1, prop='scene')
        
        left = start - self.object.worldOrientation @ Vector([0.3,0,0])
        bge.render.drawLine(start, left, [0,1,0])
        _, hitL, normL = self.object.rayCast(left, start, face=1, prop='scene')
        
        if hitR:
            tmp = hitR + (normR * Vector([0.4,0.4,0]))
            bge.render.drawLine(hitR, tmp, [1,1,0])
        if hitL:
            tmp = hitL + (normL * Vector([0.4,0.4,0]))
            bge.render.drawLine(hitL, tmp, [1,1,0])
                
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
        _, hit, norm = self.snapProp[0]
        
        if self.snapProp[1]:
            anim, start, end = self.snapProp[1]
            self.anim.actionProp[1] = (anim, start, end, 0, 1, 0)
        
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
            diff = hit - self.object.worldPosition
#                print(hit, self.object.worldPosition, diff)
            if diff.length > 0.05:
                lerp = self.object.worldPosition.lerp(hit, 0.2)
                self.object.worldPosition = lerp
            else:
                pos = 1
                
        if rot and pos:
            self.climbProp = self.snapProp[2]
            self.snapProp = 0
    
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