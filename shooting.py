import bge
from random import randint, uniform
from math import sin, cos, pi, ceil
from mathutils import Vector, Matrix
from collections import OrderedDict, defaultdict

class shooting(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ('Shooting ON/OFF', True),
        ('Recoil ON/OFF', True)
    ])
    
    def start(self, args):
        self.shootOnOff = args['Shooting ON/OFF']
        self.recoilOnOff = args['Recoil ON/OFF']
        self.camLook = self.object.scene.objects['Camera Look']
        self.startRay = self.object.scene.objects['StartPoint']
        self.endRay = self.object.scene.objects['EndPoint']
        self.hitPoint = self.object.scene.objects['HitPoint']
        
        # Components
        self.cam = self.camLook.components['camera']
        self.hud = self.object.components['hud']
        self.cont = self.object.components['controller']
        self.sound = self.object.components['sound']
        self.anim = self.object.components['animation']
        self.handhold = self.object.components['handhold']
        
        self.aimPoint = False
        self.zoomPoint = 0
        self.zoomMax = len(self.cam.focalLength)-1
        self.maxPoints = 128
#        self.increment = 0.025
        self.increment = 0.1
        self.initialSpeed = 50
#        self.initialSpeed = 1000
#        self.rayOverlap = 1.1
        self.point_list = []
        self.direction = 0
#        self.chargeFx = 0
        self.seed = 0
        self.aimtimer = 0
        self.loadout = {
            "SP": ("Pistol", 0), 
            "AR": ("Assault Rifle", 1), 
            "SG": ("Shotgun", 2), 
            "SR": ("Sniper Rifile", 3)
        }
        
        self.isAim = 0
        self.isShoot = 0
        self.isReload = 0
        self.isCock = 0
        self.isRepeat = 1
        self.isFirerate = 0
        self.isReloadrate = 0
        self.isAccurate = 5
        
        self.shoot_name = 0
        self.shoot_type = 0
        self.shoot_range = 0
        self.shoot_item = 0
        self.shoot_accuracy = 0
        self.shoot_repeat = 0
        self.shoot_firerate = 0
        self.shoot_recoil = 0
        self.shoot_shot = 0
        self.shoot_round = 0
        self.shoot_ammo = 0
        self.shoot_sfx = 0
        self.shoot_reload = 0
        
        self.getData()
        
        self.recoil_start = 0
        self.recoil_end = 0
        self.recoil_active = 0
        self.recoil_direction = 1
        self.recoil_factor = 0
        
        self.debug = [None, None]

    def update(self):
        if self.shootOnOff:
            self.toggleAim()
            self.resetShoot()
            self.startShoot()
            self.startReload()
        
        if self.recoilOnOff:
            self.startRecoil()
            
#        if self.debug:
#            bge.render.drawLine(self.debug[0][0], self.debug[0][1], (0,0,1))
#            bge.render.drawLine(self.debug[1][0], self.debug[1][1], (1,0,0))
        
    def resetShoot(self):
        if self.isAim and not self.cont.aim.active:
            self.hud.hideAll(self.hud.crosshair)
            self.hud.hideAll(self.hud.ammoPanel)
            self.hud.hideAll(self.hud.scope)
            self.cam.switchLook("R")
            self.isAim = 0
            self.zoomPoint = 0
#            self.isAccurate = 5
#            self.hud.updateCrosshairScale(self.isAccurate)
            
        if self.isShoot and not self.cont.attack.active:
            if self.isFirerate > 0:
                self.isFirerate = max(0, self.isFirerate - self.cont.dt)
                return
            
            self.isShoot = 0
            self.isRepeat = 1
            self.isFirerate = 0
            
#            self.chargeFx.endObject()
            
#            muzzle = self.object.scene.addObject("Muzzle", "Shotgun Muzzle", 30)
            
#            projectile = self.object.scene.addObject(f"Water Ball {randint(1, 4)}", self.aimPoint)
#            projectile = self.object.scene.addObject("Windbullet", self.aimPoint)
#            projectile = self.object.scene.addObject("Fireball", self.aimPoint)
#            projectile = self.object.scene.addObject("Waterball", self.aimPoint)
#            projectile = self.object.scene.addObject("Stonebullet", self.aimPoint)
#            projectile = self.object.scene.addObject("Psychoball", self.aimPoint)
#            projectile.components['projectile'].initialSpeed = self.initialSpeed
#            projectile.components['projectile'].point_list = self.point_list
#            projectile.components['projectile'].direction = self.direction
        
    def startShoot(self):
        if self.cont.aim.active:
            if not self.isAim:
                self.aimtimer = 0
                self.isAccurate = 5
                self.hud.showAll(self.hud.crosshair)
                self.hud.showAll(self.hud.ammoPanel, ("Ammo Type", self.shoot_type))
                self.anim.actionProp[2] = (f"Shoot_{self.shoot_type}", 1, 1, 0, 0, 7)
                
            self.getRayCast()
            self.startZoom()
            self.isAim = 1
            self.aimtimer += self.cont.dt
            
            if self.aimtimer > 1:
                if self.isAccurate >= self.shoot_accuracy:
                    self.isAccurate = max(self.shoot_accuracy, self.isAccurate - 10 * self.cont.dt)
                else:
                    self.isAccurate = min(self.shoot_accuracy, self.isAccurate + 10 * self.cont.dt)
            self.hud.updateCrosshairScale(self.isAccurate)
            
            if self.cont.attack.active:
                if not self.isRepeat:
                    return
                
                if self.isFirerate > 0.0:
                    self.isFirerate = max(0, self.isFirerate - self.cont.dt)
                    return
                
                if not self.shoot_ammo[0] > 0:
                    if self.cont.attack.active and self.cont.attack.activated:
                        self.sound.play(self.shoot_dry_sfx)
                    return
                
#                muzzle = self.object.scene.addObject("Muzzle", self.aimPoint, 20)
                
                self.isReload = 0
                self.isShoot = 1
                self.shoot_ammo[0] -= 1
                self.isAccurate = min(5, self.isAccurate + 2)
                self.isRepeat = self.shoot_repeat
                self.isFirerate = self.shoot_firerate
                self.anim.stopAction(2)
                self.anim.actionProp[2] = (f"Shoot_{self.shoot_type}", 1, 34, 0, 1, 0)
                
                self.sound.play(self.shoot_sfx)
                self.executeRecoil()
                hit = self.executeShoot()
                self.executeTarget(hit)
                self.hud.updateCrosshairScale(self.isAccurate)
                self.hud.updateAmmo(self.shoot_ammo)
                
    #            self.getTrajectory()
                
    #            self.chargeFx = self.object.scene.addObject("Charge", self.aimPoint)
    #            self.chargeFx.setParent(self.aimPoint)
                
    #            ball = self.object.scene.addObject("Energyball", self.object, 250)
    #            ball.components['behavior'].parent = self.object

    def executeRecoil(self):
        self.recoil_start = self.camLook.worldOrientation.to_euler()
        self.recoil_end = self.recoil_start.copy()
        self.recoil_end.x += self.shoot_recoil
        self.recoil_direction = 1
        self.recoil_active = 1

    def startRecoil(self):
        if self.recoil_active:
            if self.recoil_direction == 1:
                self.recoil_factor += 20 * self.cont.dt # Adjust the speed as needed
                if self.recoil_factor > 1:
                    self.recoil_direction = -1
            else:
                self.recoil_factor -= 10 * self.cont.dt # Adjust the speed as needed
                if self.recoil_factor < 0:
                    self.recoil_active = 0 # Stop recoil
                    
            current_euler = self.recoil_start.copy()
            current_euler.x = self.recoil_start.x + (self.recoil_end.x - self.recoil_start.x) * self.recoil_factor
            current_euler.z = self.camLook.worldOrientation.to_euler().z
            self.camLook.worldOrientation = current_euler.to_matrix()
            
    def startReload(self):
        if not self.isShoot and self.cont.reload.active and self.cont.reload.activated:
            if self.shoot_ammo[0] < self.shoot_round and self.shoot_ammo[1] > 0:
                self.isReload = True
                self.zoomPoint = 0
                self.hud.showOverlay(self.hud.scope, False)

        if self.isReload:
            if self.isReloadrate > 0.0:
                self.isReloadrate = max(0, self.isReloadrate - self.cont.dt)
                return
            
            round = self.shoot_round
            singleshot = self.shoot_type in ['HR', 'SG']
            current_ammo = self.shoot_ammo[0]
            reserve_ammo = self.shoot_ammo[1]

            if self.isCock:
                self.sound.play(self.shoot_cock_sfx)
                self.isCock = False
                self.isReload = False
                if not singleshot and current_ammo < round:
                    reload_amount = min(round - current_ammo, reserve_ammo)
                    self.shoot_ammo[1] -= reload_amount
                    self.shoot_ammo[0] += reload_amount
                    self.hud.updateAmmo(self.shoot_ammo)
                return

            if current_ammo < round and reserve_ammo > 0:
                needed_ammo = 1 if singleshot else round - current_ammo
                reload_amount = min(needed_ammo, reserve_ammo)

                self.sound.play(self.shoot_reload_sfx)
                self.isReloadrate = self.shoot_reload

                if singleshot:
                    self.shoot_ammo[1] -= reload_amount
                    self.shoot_ammo[0] += reload_amount
                    self.hud.updateAmmo(self.shoot_ammo)
                else:
                    self.isCock = True
            else:
                self.isCock = True
                
    def startZoom(self):
        if self.shoot_scope:
            if self.cont.zoomin.active and self.cont.zoomin.activated:
                if self.zoomPoint < self.zoomMax:
                    self.zoomPoint = min(self.zoomMax, self.zoomPoint + 1)
                    self.sound.play(self.shoot_zoom_sfx)
                    self.hud.showOverlay(self.hud.scope, True)
                    self.hud.showOverlay(self.hud.crosshair, False)
                
            if self.cont.zoomout.active and self.cont.zoomout.activated:
                if self.zoomPoint > 0:
                    self.zoomPoint = max(0, self.zoomPoint - 1)
                    if not self.zoomPoint:
                        self.hud.showOverlay(self.hud.scope, False)
                        self.hud.showOverlay(self.hud.crosshair, True)
                    else:
                        self.sound.play(self.shoot_zoom_sfx)

    def getRayCast(self):
        _, hit, _ = self.startRay.rayCast(self.endRay, dist=self.shoot_range, xray=1, mask=0x0005)
        self.hitPoint.worldPosition = hit if hit else self.endRay.worldPosition
        bge.render.drawLine(self.startRay.worldPosition, self.hitPoint.worldPosition, [0,0,1])
        
        self.debug[0] = (self.startRay.worldPosition.copy(), self.hitPoint.worldPosition.copy())
        return hit
    
    def getAccuracy(self):
        min = self.shoot_accuracy if not self.zoomPoint else 0
        max = self.isAccurate if not self.zoomPoint else 0
        return (min, max)
    
    def executeShoot(self):
        hit = []
        for i in range(self.shoot_shot):
            min, max = self.getAccuracy()
            max_radius = uniform(min, max)
            max_distance = 100
            distance = (self.aimPoint.worldPosition - self.hitPoint.worldPosition).length
            radius = (distance / max_distance) * max_radius
            
            seed = uniform(-pi, pi)
            x = sin(seed) * radius
            z = cos(seed) * radius
            displace  = Vector([x, 0, z])
            displace = self.hitPoint.worldOrientation @ displace
            target = self.hitPoint.worldPosition + displace
            bge.render.drawLine(self.aimPoint.worldPosition, target, [1,0,0])
            name, point, normal = self.aimPoint.rayCast(target, dist=self.shoot_range, xray=1, mask=0x0005)
            
            self.debug[1] = (self.aimPoint.worldPosition.copy(), target.copy())
            
            if name:
                hit.append((name, point, normal))
        return hit
    
    def executeTarget(self, hit):
        if hit:
            for i in hit:
                bullethit = self.object.scene.addObject(f"Bullethit", self.object, 100)
                bullethit.worldPosition = i[1]
                bullethit.alignAxisToVect(i[2], 2)
                
            sum = self.getSumDamage(hit)
            dmg = 0
            for i in sum.items():
                dmg += i[1]
                if i[0] and 'controller' in i[0]:
                    i[0].components['controller'].applyDamage(i[1])

            # test
            dmg = ceil(int(dmg))
            if dmg:
                self.hud.startExp(f"{ceil(int(dmg))}", "HIT!")
            
    def getSumDamage(self, hit):
        target = []
        for i in hit:
            if 'hit' in i[0]:
                name = i[0].parent.parent
                if not name:
                    name = i[0].parent
                target.append((name, self.shoot_damage * i[0]['hit']))
        
        sum_dict = defaultdict(int)
        for obj, value in target:
            sum_dict[obj] += value
            
        sum_dict = dict(sum_dict)
        return sum_dict 
            
    def getData(self):
        if self.isAim:
            self.aimtimer = 0
            self.isAccurate = 5
            
        if self.zoomPoint:
            self.zoomPoint = 0
            self.hud.showOverlay(self.hud.scope, False)
            
        if self.isReload:
            self.isReload = 0
            self.isCock = 0
            self.sound.stop()
        
        holding = self.handhold.holding
        data = self.handhold.loadout[holding]
        
        for key, value in data.items():
            setattr(self, f"shoot_{key}", value)
        
        self.aimPoint = self.object.scene.objects[self.shoot_item[0]].children[f"{self.shoot_name} Muzzle"]
        self.shoot_sfx = self.sound.load(data['type'])
        self.shoot_dry_sfx = self.sound.load('empty')
        self.shoot_reload_sfx = self.sound.load(f"{data['type']}_reload")
        self.shoot_cock_sfx = self.sound.load(f"{data['type']}_cock", 0.5)
        self.shoot_zoom_sfx = self.sound.load("zoom_in")
        
        self.hud.updateAmmo(self.shoot_ammo)
        self.hud.updateAmmoType(self.shoot_type)
 
    def getTrajectory(self):
        point_list = []
        mouse_hit = self.getRayCast()
        
#        self.trajectoryLine.worldPosition = mouse_hit
            
#        direction =  self.aimPoint.worldOrientation @ (Vector([0,1,0]))
        direction = mouse_hit - self.aimPoint.worldPosition
        direction.normalize()
        
        mass = 1
#        self.initialSpeed = 40
        velocity = direction * (self.initialSpeed / mass)
        position = self.aimPoint.worldPosition.copy()
        nextPosition = None
        overlap = 0
        
        point_list.append(position)
#        self.update_line_render(self.maxPoints, 0, position)

        for i in range(1, self.maxPoints):
            # Estimate velocity and update next predicted position
            velocity = self.calculate_new_velocity(velocity, 0.5, self.increment)
            nextPosition = position + velocity * self.increment

#            bge.render.drawLine(position, nextPosition, [1,1,1])
            
            # Overlap our rays by a small margin to ensure we never miss a surface
#            overlap = (position - nextPosition).length * self.rayOverlap

            # When hitting a surface, show the surface marker and stop updating our line
#            hit, hitPosition, _ = self.object.rayCast(nextPosition, position)
#            if hit:
#                point_list.append(hitPosition)
##                self.update_line_render(self.maxPoints, i, hitPosition)
###                self.move_hit_marker(hit)
#                break

            # If nothing is hit, continue rendering the arc without a visual marker
#            self.hitMarker.visible = False
            position = nextPosition
            point_list.append(position)
#            self.update_line_render(self.maxPoints, i, position)
            
#        for i in range(len(point_list) - 1):
#            bge.render.drawLine(point_list[i], point_list[i+1], [1,1,1])
            
        self.point_list = point_list
        self.direction = direction

#    def update_line_render(self, count, point, position):
#        self.trajectoryLine.worldPosition = position

    def calculate_new_velocity(self, velocity, drag, increment):
        velocity += Vector([0, 0, -9.81]) * increment
        velocity *= max(0, 1 - drag * increment)
        return velocity

    def move_hit_marker(self, hit):
        self.hitMarker.visible = True

        # Offset marker from surface
        offset = 0.025
        self.hitMarker.worldPosition = hit.hitPosition + hit.hitNormal * offset
        self.hitMarker.alignAxisToVect(hit.hitNormal, 2)
        
    def toggleAim(self):
        if self.isAim and self.cont.sprint.active and self.cont.sprint.activated:
            self.cam.camSide = "R" if self.cam.camSide == "L" else "L"
            self.cam.switchLook(self.cam.camSide)
            
    def getAmmo(self, type, reserve_ammo):
        ammo = self.handhold.loadout[self.loadout[type][1]]['ammo']
        reload_amount = 0
        
        if ammo[1] < ammo[2] and reserve_ammo > 0:
            needed_ammo = ammo[2] - ammo[1]
            reload_amount = min(needed_ammo, reserve_ammo)
            ammo[1] += reload_amount
            
            self.hud.updateAmmo(self.shoot_ammo)
            self.hud.updateMessage(f"You received {reload_amount} {self.loadout[type][0]} ammo")
            
        return reload_amount