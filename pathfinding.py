import bge
import bpy
import heapq
import random
from math import sin, cos, radians, degrees, atan2
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import OrderedDict

class pathfinding(bge.types.KX_PythonComponent):
    args = OrderedDict([
        ('Pathfinding ON/OFF', True)
    ])

    def start(self, args):
        self.pathOnOff = args['Pathfinding ON/OFF']
        
        if self.pathOnOff == True:
            self.grid_root = 30
            self.near_char = self.object.sensors['NearCharacter']
#            self.near_enem = self.object.sensors['NearEnemy']
            self.grid = self.getGridWeight(self.grid_root)
            self.path = []
            self.move_speed = 0.03
            self.start = (0, 0)
            self.target = (0, 0)
            self.runProp = 0
            self.attackProp = 0
            self.tmp = 0
        
    def update(self):
        if self.pathOnOff == True:
            self.startPathfinding()
        
    def startPathfinding(self):
        self.runProp = 0
        self.attackProp = 0
        if self.near_char.positive:
            
            target_object = self.near_char.hitObject
            dist = self.object.getDistanceTo(target_object)
            
            if dist > 10:
                # Get coordinates
                start, target = self.getCoord(target_object)
                if not self.path or target != self.target:
                    self.start = start
                    self.target = target
                    self.path = self.a_star(self.grid, self.start, self.target)

            if dist > 1.3:
                self.moveToPath(target_object, dist)
            else:
                self.attackProp = 1
            
    def moveToPath(self, target_object, dist):
        # Use index 1 of self.path so that object always look toward to next coordinates 1 step
        target = None
        if len(self.path) > 1 and dist > 15:
            target = self.getGridPosition(self.path[1])
        else:
#            target = target_object.worldPosition
            target = self.getTargetPosition()
        
        diff = target - self.object.worldPosition
        if diff.length > 2.5:
            movement = diff.normalized() * self.move_speed
            self.object.worldPosition += movement
            
            self.object.alignAxisToVect(movement, 1, 0.3)
            self.object.alignAxisToVect((0, 0, 1), 2, 1.0)
            
            self.runProp = 1
        else:
            if len(self.path) > 1:
                self.path.pop(0)
            self.runProp = 0
            
            diff = target_object.worldPosition - self.object.worldPosition
            self.object.alignAxisToVect(diff, 1, 0.3)
            self.object.alignAxisToVect((0, 0, 1), 2, 1.0)
                    
    def getCoord(self, target_object):
        start = None
        target = None
        
        for x in [self.object, target_object]:
            # Check if the ray sensor is positive
            fr = x.worldPosition
            to = fr + Vector((0, 0, -1000))
            hit_object, _, _, hit_face = x.rayCast(to, fr, xray=True, poly=1, prop='floor')
            if hit_object:
                name = hit_object.name
                obj = bpy.data.objects.get(name)
                center = Vector((0,0,0))
                vertices = [hit_face.v1, hit_face.v2, hit_face.v3, hit_face.v4]
                mesh = obj.data
                
                # Get an average position from hit face vertices
#                for vertex in vertices:
#                    center += hit_object.worldTransform @ Vector(mesh.getVertex(0, vertex).XYZ)
#                center = center / 4
                
                center = sum([obj.matrix_world @ mesh.vertices[i].co for i in vertices], Vector()) / 4
                bvh = BVHTree.FromObject(obj, bpy.context.evaluated_depsgraph_get())
                _, _, face_index, _ = bvh.find_nearest(center)
                group_name = eval(obj.vertex_groups[face_index].name)
                if x == self.object:
                    start = group_name
                else:
                    target = group_name

                # Find the vertex group of polygon with center of polygon compare to center position
#                for polygon in obj.data.polygons:
#                    if polygon.center == center:
#                        group_name = eval(obj.vertex_groups[polygon.index].name)
#                        if x == self.object:
#                            start = group_name
#                            break
#                        else:
#                            target = group_name
#                            break
                        
                # Find the nearest vertex to the hit position
#                nearest_vertex = min(obj.data.vertices, key=lambda v: (v.co - hit_position).length)
                
                # Find the vertex group with the highest weight
#                max_weight = 0.0
#                for group in nearest_vertex.groups:
#                    if group.weight > max_weight:
#                        max_weight = group.weight
#                        group_name = eval(obj.vertex_groups[group.group].name)
#                        if x == self.object:
#                            start = group_name
#                            break
#                        else:
#                            target = group_name
#                            break
        return start, target
        
    def a_star(self, grid, start, target):
#        open_set = {start}
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, target)}

        while open_set:
#            current = min(open_set, key=lambda pos: f_score[pos])
            _, current = heapq.heappop(open_set)

            if current == target:
                # Reconstruct the path from target to start
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                path.reverse()
                return path

#            open_set.remove(current)

            for neighbor in self.neighbors(current, grid):
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor, target)
#                    if neighbor not in open_set:
#                        open_set.add(neighbor)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    def neighbors(self, position, grid):
        # Return valid neighboring positions
        neighbors = []
        y, x = position
        height = len(grid)
        width = len(grid[0])

        # Define valid neighbor offsets (up, down, left, right, up-left, up-right, down-left, down-right)
        offsets = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

        for dx, dy in offsets:
            nx = x + dx
            ny = y + dy

            # Check if neighbor is within grid boundaries
            if 0 <= nx < width and 0 <= ny < height:
                # Check if the neighbor is not a wall (represented by 0 in the grid)
                if grid[nx][ny] != 0:
                    # Check if both adjacent orthogonal neighbors are passable for diagonal movement
                    orthogonal_passable = grid[x][ny] != 0 and grid[nx][y] != 0
                    if not orthogonal_passable:
                        continue

                    neighbors.append((ny, nx))

        return neighbors
    
    def heuristic(self, target, position):
        # Calculate the Manhattan distance between two positions
        return abs(position[0] - target[0]) + abs(position[1] - target[1])
    
    def getGridPosition(self, index):
        platform = bpy.data.objects['Grid']
#        vertex_groups = platform.vertex_groups
#        vertex_group_indices = {group.name: group.index for group in vertex_groups}
#        
#        group_name = str(index)
#        group_index = vertex_group_indices.get(group_name)

        # Use formula square_root * y + x
        group_index = self.grid_root * index[1] + index[0]
        center_position = platform.data.polygons[group_index].center
        
        return Vector((center_position.x, center_position.y, self.object.worldPosition.z))

#        if group_index is not None:
#            vertex_indices = [v.index for v in platform.data.vertices if group_index in [g.group for g in v.groups]]

            # Get the world coordinates of each vertex
#            vertex_positions = [platform.matrix_world @ platform.data.vertices[index].co for index in vertex_indices]

            # Get center of vertex group
#            center_position = sum(vertex_positions, Vector()) / len(vertex_positions)

            # Move object
#            return Vector((center_position.x, center_position.y, self.object.worldPosition.z))
        
    def getGridWeight(self, length):
        obj = bpy.data.objects.get('Grid')
        
        if obj and obj.type == 'MESH' and obj.data:
            mesh = obj.data
            max_weights = {}

            # Iterate over the vertices
            for vertex in mesh.vertices:
                # Get the vertex groups and weights for the current vertex
                vertex_weights = vertex.groups

                # Iterate over the vertex groups and weights
                for vertex_weight in vertex_weights:
                    group_index = vertex_weight.group
                    weight = vertex_weight.weight

                    # Update the maximum weight for the group index
                    max_weights[group_index] = weight

            grid_weight = []
            temp = []
            for i, weight in enumerate(max_weights.values()):
                if i % length != length - 1:
                    temp.append(weight)
                else:
                    temp.append(weight)
                    grid_weight.append(temp)
                    temp = []
                    
            return grid_weight
        
    def getTargetPosition(self):
        lv = 4
        target = self.near_char.hitObject
        radius = lv * ((self.tmp//lv)+1)
        deg = 360 / lv
        if self.tmp < lv:
            radian = (radians(deg) * self.tmp)
        else:
            radian = self.getNearestRadian(target)
            
        x = cos(radian) * radius
        y = sin(radian) * radius

        # Calculate the new position based on character's orientation
        target_rot = target.worldOrientation

        # Update x and y based on character's orientation
#        x_offset = target_rot.col[1][0] * x + target_rot.col[1][1] * y
#        y_offset = target_rot.col[0][0] * x + target_rot.col[0][1] * y
        x_offset = x
        y_offset = y

        # Set the Cube's worldPosition to the new position
#        self.object.worldPosition.x = target.worldPosition.x + x_offset
#        self.object.worldPosition.y = target.worldPosition.y + y_offset
        return Vector([target.worldPosition.x + x_offset, target.worldPosition.y + y_offset, 0])
        
    def getNearestRadian(self, target):
        # Target position (x, y)
        target_x = target.worldPosition.x  # Replace with the actual target position
        target_y = target.worldPosition.y  # Replace with the actual target position

        # Object's position (x, y)
        object_x = self.object.worldPosition.x  # Replace with the actual object's position
        object_y = self.object.worldPosition.y  # Replace with the actual object's position

        # Calculate the vector from the object to the target
        delta_x = object_x - target_x 
        delta_y = object_y - target_y

        # Calculate the radian (angle) using atan2
        radian = atan2(delta_y, delta_x)

        # Convert radian to degrees if needed
#        deg = degrees(radian)

#        print("Radian:", radian)
#        print("Degrees:", deg)
        
        return radian
    
    def getRunProp(self):
        return self.runProp
    
    def getAttackProp(self):
        return self.attackProp