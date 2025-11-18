
import bpy
import config_para as cfg

def add_shape_key(obj, name):
    # Ensure Basis exists
    if obj.data.shape_keys is None:
        obj.shape_key_add(name=cfg.BASIS, from_mix=False)

    # Add new key
    key = obj.shape_key_add(name=name, from_mix=False)

    # Activate it
    idx = obj.data.shape_keys.key_blocks.find(name)
    obj.active_shape_key_index = idx

    return name

def animate_shape_keys(obj, shape_key_list,
                       start_frame=1,
                       stage_length=40,
                       fade=10):
    key_blocks = obj.data.shape_keys.key_blocks

    current_frame = start_frame

    for key_name in shape_key_list:
        key = key_blocks[key_name]

        # fade in
        key.value = 0.0
        key.keyframe_insert("value", frame=current_frame)

        key.value = 1.0
        key.keyframe_insert("value", frame=current_frame + fade)

        # hold
        key.value = 1.0
        key.keyframe_insert("value", frame=current_frame + stage_length - fade)

        # fade out
        key.value = 0.0
        key.keyframe_insert("value", frame=current_frame + stage_length)

        current_frame += stage_length


