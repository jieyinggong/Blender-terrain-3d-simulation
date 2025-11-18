import bpy

import config_para as cfg
import animation

def render_terrain_color(terrain_obj):
    # Calculate terrain height range
    z_values = [v.co.z for v in terrain_obj.data.vertices]
    z_min, z_max = min(z_values), max(z_values)
    print(f"Detected terrain height range: {z_min:.3f} to {z_max:.3f}")

    # Material and nodes setup
    material = bpy.data.materials.new(name="HeightGradient_Material")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    # Node definition
    output_node = nodes.new("ShaderNodeOutputMaterial")
    bsdf_node = nodes.new("ShaderNodeBsdfPrincipled")
    texcoord_node = nodes.new("ShaderNodeTexCoord")
    sep_xyz_node = nodes.new("ShaderNodeSeparateXYZ")
    map_range_node = nodes.new("ShaderNodeMapRange")
    math_pow_node = nodes.new("ShaderNodeMath")
    color_ramp_node = nodes.new("ShaderNodeValToRGB")

    # Node layout positions
    output_node.location = (800, 0)
    bsdf_node.location = (600, 0)
    color_ramp_node.location = (400, 0)
    math_pow_node.location = (200, 0)
    map_range_node.location = (0, 0)
    sep_xyz_node.location = (-200, 0)
    texcoord_node.location = (-400, 0)

    # Node parameter settings
    bsdf_node.inputs["Roughness"].default_value = 0.9
    bsdf_node.inputs["Specular IOR Level"].default_value = 0.2

    map_range_node.inputs['From Min'].default_value = z_min + (z_max - z_min) * 0.15
    map_range_node.inputs['From Max'].default_value = z_min + (z_max - z_min) * 0.85
    map_range_node.inputs['To Min'].default_value = 0.0
    map_range_node.inputs['To Max'].default_value = 1.0

    math_pow_node.operation = 'POWER'
    math_pow_node.inputs[1].default_value = cfg.POWER_EXPONENT

    # Color ramp config
    color_ramp = color_ramp_node.color_ramp
    color_ramp.interpolation = cfg.COLOR_INTERPOLATION
    color_ramp.elements[0].color = (0.03, 0.1, 0.03, 1.0)  # Low elevation - green
    mid_element = color_ramp.elements.new(0.55)
    mid_element.color = (0.075, 0.1, 0.045, 1.0)  # Mid elevation - brown
    color_ramp.elements[1].position = 0.85
    color_ramp.elements[1].color = (0.9, 0.9, 0.9, 1.0)  # High elevation - snow

    # Node connections
    links.new(texcoord_node.outputs["Object"], sep_xyz_node.inputs["Vector"])
    links.new(sep_xyz_node.outputs["Z"], map_range_node.inputs["Value"])
    links.new(map_range_node.outputs["Result"], math_pow_node.inputs[0])
    links.new(math_pow_node.outputs["Value"], color_ramp_node.inputs["Fac"])
    links.new(color_ramp_node.outputs["Color"], bsdf_node.inputs["Base Color"])
    links.new(bsdf_node.outputs["BSDF"], output_node.inputs["Surface"])

    # Apply material to terrain
    if terrain_obj.data.materials:
        terrain_obj.data.materials[0] = material
    else:
        terrain_obj.data.materials.append(material)

    animation.add_shape_key(terrain_obj, cfg.RENDER_COLOR)

    print("Material applied successfully")
    print(f"Nonlinear exponent: {cfg.POWER_EXPONENT}, interpolation: {cfg.COLOR_INTERPOLATION}")