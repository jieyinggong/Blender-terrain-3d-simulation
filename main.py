import os
import sys

import bpy
import importlib

current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.append(current_dir)

print("Added to sys.path:", current_dir)

print("Importing modules...")
print("Current working directory:", os.getcwd())
print("__file_:", __file__)

import create
import generate_terrian as generate
import modifier
import render_color as render
import animation
import config_para as cfg

# check module paths
# print("create module path:", create.__file__)
# print("generate_terrian module path:", generate.__file__)
# print("modifier module path:", modifier.__file__)
# print("render_color module path:", render.__file__)
# print("config_para module path:", cfg.__file__)

print("Modules imported successfully.")

# Force reload 
importlib.reload(create)
importlib.reload(generate)
importlib.reload(modifier)
importlib.reload(animation)
importlib.reload(render)
importlib.reload(cfg)

# check main
print("__name__:", __name__)

def main():

    print("Starting terrain generation...")

    collection = create.ensure_collection(cfg.COLLECTION_NAME)
    create.purge_collection_objects(collection)

    terrain = create.create_flat_terrain()

    create.link_object_to_collection(collection, terrain)

     # Add colors and wireframe
    create.add_material_color(terrain, (0.1, 0.6, 0.1))  # Green terrain
    create.add_wireframe_modifier(terrain, wireframe_thickness=0.02) # Wireframe for terrain

    print("Plane created")
    print(f"Terrain: {terrain.name} (size=±{cfg.TERRAIN_SIZE}, resolution={cfg.TERRAIN_RESOLUTION})")

    # Deform terrain
    generate.deform_terrain(terrain, terrain_mode="mountain")
    print("Terrain deformed")

    # add noise
    # Apply disturbances
    generate.apply_smart_jitter(terrain)
    generate.smooth_height_by_slope(terrain)
    bpy.context.view_layer.update()
   # print("Terrain generation and disturbance overlay successful")

    # Modify terrain with modifiers
    modifier.modify_terrain(terrain)

    # Render terrain color
    render.render_terrain_color(terrain)

    animation.animate_shape_keys(terrain, cfg.SHAPE_KEY_ORDER)

    print("Terrain setup complete!")

# explicitly call main function
main()