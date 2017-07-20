from placeSensors import generateWholeSkin

VERTICES = ["rArm_skin.raw",
            "head.raw",
            "torso_skin.raw",
            "lArm_skin.raw"
            ]
SENSOR_SIZES = ["0.013 0.013 0.001",
                "0.013 0.013 0.001",
                "0.013 0.013 0.001",
                "0.013 0.013 0.001"]
SENSOR_NAMES = ["skin_r_wrist",
                "skin_head",
                "skin_torso",
                "skin_l_wrist"]
LINK_NAMES = ["r_wrist",
              "Head",
              "base_link",
              "l_wrist"]
ORIG_FILE = '/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig_sdf.sdf'
OUTPUT_FILE = '/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.sdf'

generateWholeSkin(verticesFiles=VERTICES,
                  sensorSizes=SENSOR_SIZES,
                  sensorNames=SENSOR_NAMES,
                  linkNames=LINK_NAMES,
                  origFile=ORIG_FILE,
                  outputFile=OUTPUT_FILE)