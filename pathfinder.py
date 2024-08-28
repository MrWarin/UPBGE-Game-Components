import bge
import bpy
import mathutils
# A* Pathfinding Algorithm with Wall Detection

def heuristic(target, position):
    # Calculate the Manhattan distance between two positions
    return abs(position[0] - target[0]) + abs(position[1] - target[1])

def a_star(grid, start, target):
    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, target)}

    while open_set:
        current = min(open_set, key=lambda pos: f_score[pos])

        if current == target:
            # Reconstruct the path from target to start
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        open_set.remove(current)

        for neighbor in neighbors(current, grid):
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, target)
                if neighbor not in open_set:
                    open_set.add(neighbor)
    return None

def neighbors(position, grid):
    # Return valid neighboring positions
    neighbors = []
    y, x = position
    height = len(grid)
    width = len(grid[0])
    
    # Define valid neighbor offsets (up, down, left, right)
    offsets = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    for dx, dy in offsets:
        nx = x + dx
        ny = y + dy
        
        # Check if neighbor is within grid boundaries
        if 0 <= nx < width and 0 <= ny < height:
            # Check if the neighbor is not a wall (represented by 0 in the grid)
            if grid[nx][ny] != 0:
                neighbors.append((ny, nx))
    
    return neighbors

# Example usage
grid = [
    [1, 0, 1, 1, 1, 0, 1, 1, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [1, 1, 1, 0, 1, 1, 1, 0, 1, 1]
]

start = (0, 0)
target = (9, 9)
path = a_star(grid, start, target)

cont = bge.logic.getCurrentController()
object = cont.owner
scene = bge.logic.getCurrentScene()
platform = bpy.data.objects['Grid']
prop = object['prop']

if prop < len(path):
    group = platform.vertex_groups[str(path[prop])]
    vertex_indices = [v.index for v in platform.data.vertices if group.index in [g.group for g in v.groups]]

    # Get the world coordinates of each vertex
    vertex_positions = [platform.matrix_world @ platform.data.vertices[index].co for index in vertex_indices]

    # Get center of vertex group
#    center_position = mathutils.Vector()
#    for position in vertex_positions:
#        center_position += position
#    center_position /= len(vertex_positions)
    center_position = sum(vertex_positions, mathutils.Vector()) / len(vertex_positions)

    # Move object
    if round(object.worldPosition.x, 1) == round(center_position.x, 1) and round(object.worldPosition.y, 1) == round(center_position.y, 1):
#        object['prop'] = object['prop']+1
        object['prop'] += 1
    else:
#        diff = object.worldPosition - center_position
#        pos = object.worldPosition.copy()
#        pos = pos - (diff / 10)
#        object.worldPosition = pos
        diff = object.worldPosition - center_position
        object.worldPosition -= diff / 10