import bpy
import config_para as cfg
import animation

def modify_terrain(terrain_obj):
    bpy.context.view_layer.objects.active = terrain_obj
    terrain_obj.select_set(True)

    # Clean up existing modifiers to avoid duplication
    modifier_names = ["MicroDisplace", "SmoothTerrain"]
    for modifier_name in modifier_names:
        if modifier_name in terrain_obj.modifiers:
            terrain_obj.modifiers.remove(terrain_obj.modifiers[modifier_name])
  
    # Add displace modifier
    # Create vertex group
    vertex_group = terrain_obj.vertex_groups.new(name="PeakMask")

    # Assign vertices to group based on height
    height_threshold = 20.0
    for vertex in terrain_obj.data.vertices:
        if vertex.co.z > height_threshold:
            vertex_group.add([vertex.index], 1.0, 'ADD')  # Full weight for high vertices
        else:
            vertex_group.add([vertex.index], 0.3, 'ADD')  # Low weight for low vertices

    # Create displace modifier and assign vertex group
    displace_modifier = terrain_obj.modifiers.new("LocalDisplace", "DISPLACE")
    displace_modifier.vertex_group = vertex_group.name

    # Configure noise texture
    cloud_texture = bpy.data.textures.new("PeakNoise", "CLOUDS")
    cloud_texture.noise_scale = 1.2
    displace_modifier.texture = cloud_texture
    displace_modifier.strength = 2
    displace_modifier.mid_level = 0.2
    displace_modifier.direction = 'Z'

    print("Added Displace Modifier with Cloud texture")

    # Apply the modifier as a new shape key
    bpy.ops.object.modifier_apply_as_shapekey(modifier=displace_modifier.name)

    # rename new shape key
    new_key = terrain_obj.data.shape_keys.key_blocks[-1]
    new_key.name = cfg.MODIFY_TERRAIN
    
    print(f"Baked modifiers into shape key: {new_key.name}")
    terrain_obj.modifiers.clear()

    terrain_obj.data.update()
    print("modify_terrain shape key complete:", new_key.name)
    print("=== DEBUG: ALL SHAPE KEYS ===")
    for key in terrain_obj.data.shape_keys.key_blocks:
        print("   ", key.name)

    print("Terrain modifiers applied successfully")