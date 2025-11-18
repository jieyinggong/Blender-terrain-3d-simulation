import bpy
import math
import random
import bmesh
import numpy as np
from mathutils import Vector

import config_para as cfg
import animation


# helpers 
    
def compute_slope(terrain_obj, shape_key=None):
    """Calculate local slope for each vertex using BMesh"""
    bmesh_data = bmesh.new()
    bmesh_data.from_mesh(terrain_obj.data)
    bm_verts = bmesh_data.verts

    vertex_count = len(bm_verts)
    slope_values = np.zeros(vertex_count)

    if shape_key:
        coords = [v.co.copy() for v in shape_key.data]  # shape key 
    else:
        coords = [v.co.copy() for v in terrain_obj.data.vertices]  # mesh

    for i, bm_vert in enumerate(bm_verts):
        neighbors = [edge.other_vert(bm_vert) for edge in bm_vert.link_edges]

        if not neighbors:
            continue
        height_diff = np.mean([abs(neighbor.co.z - bm_vert.co.z) for neighbor in neighbors])
        slope_values[i] = height_diff

    # Clean up BMesh memory
    bmesh_data.free()

    # Normalize slope values
    slope_min, slope_max = slope_values.min(), slope_values.max()
    slope_values = (slope_values - slope_min) / (slope_max - slope_min + 1e-6)
    return slope_values

def compute_height_normalization(terrain_obj, shape_key = None):
    """Normalize height values to 0-1 range"""
    data = shape_key.data if shape_key else terrain_obj.data.vertices
    print("debug: use shape key or terrian", shape_key is not None)
    z_coordinates = [vertex.co.z for vertex in data]
    z_min, z_max = min(z_coordinates), max(z_coordinates)
    z_range = max(z_max - z_min, 1e-6)
    return [(z - z_min) / z_range for z in z_coordinates]

def compute_jitter_weight(height_norms, slope_values, height_weight=0.6, slope_weight=0.4, 
                         height_exponent=1.0, slope_exponent=1.0):
    """Calculate mixed disturbance weight: w = a*h^alpha + b*s^beta"""
    weights = []
    for height, slope in zip(height_norms, slope_values):
        weight = height_weight * (height ** height_exponent) + slope_weight * (slope ** slope_exponent)
        weights.append(min(weight, 1.0))
    return weights

# Asymmetric disturbance function
def asymmetric_jitter(x, y, intensity=cfg.RANDOMNESS_FACTOR):
    """Generate natural asymmetric Z disturbance for realistic terrain variation"""
    # Local random seed for consistent coordinates
    random.seed(int(x * 11.17 + y * 5.31 + 11))
    # Multi-layer noise overlay (fractal brownian motion style)
    noise_1 = math.sin(0.05 * x) * math.cos(0.08 * y)
    noise_2 = math.sin(0.15 * x + 0.3) * math.cos(0.1 * y + 1.2)
    noise_3 = math.sin(0.4 * x - 0.7 * y)

    # Local random variation
    local_randomness = random.uniform(-1, 1) * 0.6
    # Weighted combination of multiple frequencies and randomness
    combined_value = (0.5 * noise_1 + 0.3 * noise_2 + 0.2 * noise_3 + local_randomness)
    # Enhance asymmetry
    return max(-1.0, min(1.0, combined_value)) * intensity


# actual terrain functions

def deform_terrain(terrain_obj, terrain_mode="mountain"):
    """Generate base terrain with different modes"""

    key_name = animation.add_shape_key(terrain_obj, cfg.DEFORM_TERRAIN)
    key_block = terrain_obj.data.shape_keys.key_blocks[key_name]

    for i, vertex in enumerate(key_block.data):
        x, y = vertex.co.x, vertex.co.y
        radius = math.sqrt(x**2 + y**2)

        # Different modes control terrain shape
        if terrain_mode == "mountain":
            base_height = abs(math.sin(cfg.FREQUENCY * x + cfg.PHASE_X) * math.cos(cfg.FREQUENCY * y + cfg.PHASE_Y)
                            + cfg.MIX_WEIGHT * math.sin(cfg.MIX_FREQUENCY * cfg.FREQUENCY * y + cfg.PHASE_MIX) + cfg.PHASE_Z)
            z = cfg.HEIGHT_SCALE * base_height**cfg.POWER_VALUE * math.exp(-cfg.DECAY_RATE * radius**2)
        else:
            z = 0.0

        vertex.co.z = max(z, 0.0)

    terrain_obj.data.update()
    print(f"Base terrain generation completed: mode = {terrain_mode}")

def apply_smart_jitter(terrain_obj,jitter_intensity=3, height_weight=0.6, slope_weight=0.4,
                      height_exponent=1.2, slope_exponent=1.2, noise_strength=5):
    """Apply disturbance based on height and slope: higher and steeper areas get more variation"""

    key_name = animation.add_shape_key(terrain_obj, cfg.APPLY_JITTER)
    keys = terrain_obj.data.shape_keys.key_blocks  

    prev_key = keys[-2]      
    key_block = keys[-1]   

    print("debug: key names:", prev_key.name, key_block.name)   

    height_norms = compute_height_normalization(terrain_obj, prev_key)
    slope_values = compute_slope(terrain_obj, prev_key)
    weights = compute_jitter_weight(height_norms, slope_values, height_weight, slope_weight, 
                                  height_exponent, slope_exponent)


    for i in range(len(prev_key.data)):
        x, y, z = prev_key.data[i].co
        geometric_jitter = (random.random() - 0.5) * 2.0 * jitter_intensity * weights[i]
        spatial_jitter = asymmetric_jitter(x, y)
        combined_jitter = geometric_jitter * (1 + noise_strength * spatial_jitter)
        if combined_jitter + z < 0:
            combined_jitter = -z  # prevent going below zero height
        key_block.data[i].co.z = combined_jitter

    terrain_obj.data.update()
    print("Height and slope dependent jitter applied111")    

def smooth_height_by_slope(terrain_obj, base_smoothing_factor=0.1, slope_exponent=2, iteration_count=3):
    """Apply stronger smoothing to vertices with lower slope"""
    key_name = animation.add_shape_key(terrain_obj, cfg.SMOOTH_TERRAIN)
    keys = terrain_obj.data.shape_keys.key_blocks

    prev_key = keys[-2]
    key_block = keys[-1]

    bmesh_data = bmesh.new()
    bmesh_data.from_mesh(terrain_obj.data)

    bmesh_data.verts.ensure_lookup_table()
    bmvert = bmesh_data.verts
    slope_values = compute_slope(terrain_obj)

    z_values = np.array([p.co.z for p in prev_key.data])
    slope_values = compute_slope(terrain_obj, prev_key)

    for _ in range(iteration_count):
        new_z_values = np.zeros(len(bmvert))
        for i, vert_prev in enumerate(prev_key.data):
            neighbors = [edge.other_vert(bmvert[i]) for edge in bmvert[i].link_edges]
            if not neighbors:
                new_z_values[i] = vert_prev.co.z
                continue

            # Average height of neighbors
            neighbor_avg_height = np.mean([prev_key.data[n.index].co.z for n in neighbors])

            # Slope weight control
            slope = slope_values[i]
            smoothing_weight = base_smoothing_factor * (1 - slope**slope_exponent)

            # Linear interpolation between original and neighbor average
            new_z_values[i] = (1 - smoothing_weight) * vert_prev.co.z + smoothing_weight * neighbor_avg_height

        # Apply updates
        for i, p in enumerate(key_block.data):
            p.co.z = new_z_values[i] - prev_key.data[i].co.z

    bmesh_data.free()
    terrain_obj.data.update()
    print("Slope-dependent smoothing applied")
