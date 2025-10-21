import bpy
import bmesh
from mathutils import Vector

# Configuration parameters
COLLECTION_NAME = "MountainDemo"
TERRAIN_OBJECT_NAME = "Terrain"
PLATFORM_NAME = "LandingPad"

# Terrain parameters
TERRAIN_SIZE = 60.0
TERRAIN_RESOLUTION = 120


def ensure_collection(collection_name: str) -> bpy.types.Collection:
    """Ensure collection exists and set as active"""
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(collection)
    # Set as active collection
    bpy.context.view_layer.active_layer_collection = next(
        (layer_coll for layer_coll in bpy.context.view_layer.layer_collection.children 
         if layer_coll.collection == collection),
        bpy.context.view_layer.layer_collection
    )
    return collection

def purge_collection_objects(collection: bpy.types.Collection):
    """Clear all objects in collection for script reusability"""
    for obj in list(collection.objects):
        collection.objects.unlink(obj)
        if not obj.users_collection:
            bpy.data.objects.remove(obj, do_unlink=True)
    for datablock in [bpy.data.meshes]:
        for mesh in list(datablock):
            if mesh.users == 0:
                datablock.remove(mesh)

def link_object_to_collection(collection: bpy.types.Collection, obj: bpy.types.Object):
    """Link object to specified collection"""
    if obj.name not in collection.objects:
        collection.objects.link(obj)

def add_material_color(obj, color):
    """Add basic material color to object for visual distinction"""
    material = bpy.data.materials.new(name=f"{obj.name}_Material")
    material.diffuse_color = (*color, 1.0)
    obj.data.materials.append(material)
    
def add_wireframe_modifier(obj, wireframe_thickness=0.02):
    """Add wireframe modifier with black material"""
    # Add second black material for wireframe
    if len(obj.data.materials) < 2:
        wireframe_material = bpy.data.materials.new(name="WireframeMaterial_Black")
        wireframe_material.use_nodes = True
        bsdf_node = wireframe_material.node_tree.nodes["Principled BSDF"]
        bsdf_node.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)
        bsdf_node.inputs["Roughness"].default_value = 1.0
        obj.data.materials.append(wireframe_material)

    # Create wireframe modifier
    wireframe_modifier = obj.modifiers.new(name="WireframeView", type='WIREFRAME')
    wireframe_modifier.thickness = wireframe_thickness
    wireframe_modifier.use_replace = False
    wireframe_modifier.material_offset = 1

# Terrain creation functions
def create_flat_terrain(size=TERRAIN_SIZE, resolution=TERRAIN_RESOLUTION) -> bpy.types.Object:
    """Generate flat plane mesh centered at origin"""
    mesh = bpy.data.meshes.new(f"{TERRAIN_OBJECT_NAME}Mesh")
    terrain_obj = bpy.data.objects.new(TERRAIN_OBJECT_NAME, mesh)
    bmesh_data = bmesh.new()

    # Create vertices
    for j in range(resolution + 1):
        y = (j / resolution - 0.5) * (2 * size)
        for i in range(resolution + 1):
            x = (i / resolution - 0.5) * (2 * size)
            bmesh_data.verts.new((x, y, 0.0))
    bmesh_data.verts.ensure_lookup_table()

    # Create faces
    def vertex_id(i, j): 
        return j * (resolution + 1) + i
    
    for j in range(resolution):
        for i in range(resolution):
            v0 = bmesh_data.verts[vertex_id(i, j)]
            v1 = bmesh_data.verts[vertex_id(i+1, j)]
            v2 = bmesh_data.verts[vertex_id(i+1, j+1)]
            v3 = bmesh_data.verts[vertex_id(i, j+1)]
            bmesh_data.faces.new((v0, v1, v2, v3))

    bmesh_data.to_mesh(mesh)
    bmesh_data.free()
    mesh.update()
    return terrain_obj

def main():
    collection = ensure_collection(COLLECTION_NAME)
    purge_collection_objects(collection)

    terrain = create_flat_terrain()

    link_object_to_collection(collection, terrain)

    # Add colors and wireframe
    add_material_color(terrain, (0.1, 0.6, 0.1))  # Green terrain
    add_wireframe_modifier(terrain, wireframe_thickness=0.02) # Wireframe for terrain

    print("Plane created")
    print(f"Terrain: {terrain.name} (size=±{TERRAIN_SIZE}, resolution={TERRAIN_RESOLUTION})")
 

if __name__ == "__main__":
    main()