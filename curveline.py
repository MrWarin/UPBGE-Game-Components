import bge
from mathutils import Vector, Matrix
from collections import OrderedDict

class curveline(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        self.camLook = self.object.scene.objects["Camera Look"]
        self.cam = self.object.scene.objects["Camera"]
        self.start = self.object.scene.objects["StartPoint"]
        self.end = self.object.scene.objects["EndPoint"]
        self.point1 = self.object.scene.objects["AimPoint"]
        self.point2 = self.object.scene.objects["HitPoint"]
        self.point3 = self.object.scene.objects["Point3"]
        self.dot = self.object.scene.objects["Dot"]
        self.vertex_count = 12

    def update(self):
        point_list = []

        for ratio in range(self.vertex_count + 1):
            ratio = ratio / self.vertex_count
            
            _, mouse_hit, _ = self.start.rayCast(self.end.worldPosition, face=1)
            
            self.point2.worldPosition = self.end.worldPosition
            if not mouse_hit:
                mouse_hit = self.point2.worldPosition
            
            self.dot.worldPosition = mouse_hit
            
#            rotation_matrix = self.camLook.worldOrientation.copy()
#            rotation_matrix.col[2] = Vector([0, 0, 1])
#            far = mouse_hit + (rotation_matrix @ Vector([0,100,1]))
#            target = far - Vector([0,0,90])
#            bge.render.drawLine(far, target, [0,0,1])
#            _, hit_position, _ = self.object.rayCast(target, far, face=1)
            
            tangent_line_vertex1 = self.point1.worldPosition.lerp(mouse_hit, ratio)
            bge.render.drawLine(self.point1.worldPosition, mouse_hit, [1,0,0])
            
            rotation_matrix = self.camLook.worldOrientation.copy()
#            rotation_matrix.col[2] = Vector([0, 0, 1])
            far = self.point3.worldPosition + (rotation_matrix @ Vector([0,0,0]))
            
            tangent_line_vertex2 = self.point2.worldPosition.lerp(self.point3.worldPosition, ratio)
            bge.render.drawLine(self.point2.worldPosition, self.point3.worldPosition, [0,0,1])
            
            bezier_point = tangent_line_vertex1.lerp(tangent_line_vertex2, ratio)
#            bge.render.drawLine(tangent_line_vertex1, tangent_line_vertex2, [1,1,1])

            point_list.append(bezier_point)

        for i in range(len(point_list) - 1):
            bge.render.drawLine(point_list[i], point_list[i+1], [1,1,1])
            
            
import bge
from mathutils import Vector, Matrix
from collections import OrderedDict

class shooting(bge.types.KX_PythonComponent):
    # Put your arguments here of the format ("key", default_value).
    # These values are exposed to the UI.
    args = OrderedDict([
    ])

    def start(self, args):
        self.start = self.object.scene.objects["StartPoint"]
        self.end = self.object.scene.objects["EndPoint"]
        self.point1 = self.object.scene.objects["AimPoint"]
        self.point2 = self.object.scene.objects["HitPoint"]
        self.dot = self.object.scene.objects["Dot"]

    def update(self):
            
        _, mouse_hit, _ = self.start.rayCast(self.end.worldPosition, face=1)
        
        self.point2.worldPosition = self.end.worldPosition
        
        if not mouse_hit:
            mouse_hit = self.point2.worldPosition
            
        self.dot.worldPosition = mouse_hit
        bge.render.drawLine(self.point1.worldPosition, mouse_hit, [1,0,0])