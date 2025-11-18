import bpy

import config_para as cfg
import animation

def get_final_height_range(obj):
    key = obj.data.shape_keys.key_blocks[cfg.DEFORM_TERRAIN]
    z_values = [p.co.z for p in key.data]
    return min(z_values), max(z_values)

def render_terrain_color(terrain_obj):
    z_min, z_max = get_final_height_range(terrain_obj)
    z_max = 1.05 * z_max  # Slightly extend max for better color gradation
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

    color_ramp.elements[0].position = 0.0
    color_ramp.elements[0].color = (0.02, 0.09, 0.02, 1.0)

    # 4 color stops
    e1 = color_ramp.elements.new(0.45)
    e2 = color_ramp.elements.new(0.8)
    e3 = color_ramp.elements.new(1.00)

    # Set colors
    e1.color = (0.2, 0.08, 0.02, 1.0)   # Dirt Brown
    e2.color = (0.5, 0.4, 0.4, 1.0)   # Rocky Gray
    e3.color = (0.9, 0.9, 0.9, 1.0)      # Snow White

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


    print("Material applied successfully")
    print(f"Nonlinear exponent: {cfg.POWER_EXPONENT}, interpolation: {cfg.COLOR_INTERPOLATION}")

    return {
        "tree": material.node_tree,
        "bsdf": bsdf_node,
        "output": output_node
    }

def setup_mixshader_fade(tree, bsdf_node, output_node):
    nodes = tree.nodes
    links = tree.links

    # White Shader (Shader1)
    white = nodes.new("ShaderNodeBsdfDiffuse")
    white.location = (600, -200)
    white.inputs["Color"].default_value = (0.15, 0.15, 0.15, 1)

    # MixShader
    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (900, -100)
    mix.inputs["Fac"].default_value = 0.0  # Start with white

    # Connect White → Mix.Shader1
    links.new(white.outputs["BSDF"], mix.inputs[1])

    # Connect Colored BSDF → Mix.Shader2
    links.new(bsdf_node.outputs["BSDF"], mix.inputs[2])

    # MixShader → Output
    links.new(mix.outputs["Shader"], output_node.inputs["Surface"])

    print("[MixShader] Created material fade setup.")

    return mix