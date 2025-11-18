import bpy
import config_para as cfg
import animation

def modify_terrain(terrain_obj):
    # Clean up existing modifiers to avoid duplication
    modifier_names = ["MicroDisplace", "SmoothTerrain"]
    for modifier_name in modifier_names:
        if modifier_name in terrain_obj.modifiers:
            terrain_obj.modifiers.remove(terrain_obj.modifiers[modifier_name])

    # Add displace modifier
    # Create vertex group
    vertex_group = terrain_obj.vertex_groups.new(name="PeakMask")

    # Assign vertices to group based on height
    height_threshold = 10.0
    for vertex in terrain_obj.data.vertices:
        if vertex.co.z > height_threshold:
            vertex_group.add([vertex.index], 1.0, 'ADD')  # Full weight for high vertices
        else:
            vertex_group.add([vertex.index], 0.1, 'ADD')  # Low weight for low vertices

    # Create displace modifier and assign vertex group
    displace_modifier = terrain_obj.modifiers.new("LocalDisplace", "DISPLACE")
    displace_modifier.vertex_group = vertex_group.name

    # Configure noise texture
    cloud_texture = bpy.data.textures.new("PeakNoise", "CLOUDS")
    cloud_texture.noise_scale = 1.2
    displace_modifier.texture = cloud_texture
    displace_modifier.strength = 1.5
    displace_modifier.mid_level = 0.2
    displace_modifier.direction = 'Z'

    print("Added Displace Modifier with Cloud texture")

    # Add smooth modifier
    smooth_modifier = terrain_obj.modifiers.new("SmoothTerrain", "SMOOTH")
    smooth_modifier.factor = 0.2
    smooth_modifier.iterations = 5
    smooth_modifier.use_x = True
    smooth_modifier.use_y = True
    smooth_modifier.use_z = True

    print("Added Smooth Modifier")

    # smooth after displace
    terrain_obj.modifiers.move(len(terrain_obj.modifiers)-1, 0)

    animation.add_shape_key(terrain_obj, cfg.MODIFY_TERRAIN)

    print("Terrain modifiers applied successfully")