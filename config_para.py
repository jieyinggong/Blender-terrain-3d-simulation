
# create
# Configuration parameters
COLLECTION_NAME = "MountainDemo"
TERRAIN_OBJECT_NAME = "Terrain"
PLATFORM_NAME = "LandingPad"

# Terrain parameters
TERRAIN_SIZE = 60.0
TERRAIN_RESOLUTION = 120

# generate
TERRAIN_MODE = "mountain"   
HEIGHT_SCALE = 2.5
FREQUENCY = 0.15 # default 0.15
POWER_VALUE = 1.5 # default 1.5
DECAY_RATE = 0.001 # default 0.0008
PHASE_X = -1
PHASE_Y = 0.7
PHASE_Z = 0.05
MIX_WEIGHT = 0.5 # default 0.5
MIX_FREQUENCY = 1.8 # default 1.8
PHASE_MIX = 0

RANDOMNESS_FACTOR = 0.4 # default 0.4  

# render
# Configuration parameters
POWER_EXPONENT = 1.7
COLOR_INTERPOLATION = 'B_SPLINE'

#animation
#key names
BASIS = "Basis"
DEFORM_STAGE1 = "StageBaseWave"
DEFORM_STAGE2 = "StageMixNoise"
DEFORM_STAGE3 = "StagePowerShape"
DEFORM_STAGE4 = "StageRadialDecay"
APPLY_JITTER = "ApplyJitter"
SMOOTH_TERRAIN = "SmoothTerrain"
MODIFY_TERRAIN = "ModifyTerrain"
RENDER_COLOR = "RenderColor"

SHAPE_KEY_ORDER = [
    BASIS,
    DEFORM_STAGE1,
    DEFORM_STAGE2,
    DEFORM_STAGE3,
    DEFORM_STAGE4,
    APPLY_JITTER,   
    SMOOTH_TERRAIN,
    MODIFY_TERRAIN,
]