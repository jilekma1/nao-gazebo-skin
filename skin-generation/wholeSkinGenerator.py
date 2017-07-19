from placeSensors import generateWholeSkin

VERTICES = ["rArm_skin.raw", "head.raw"]
SENSOR_SIZES = ["0.002 0.002 0.001", "0.01 0.01 0.001"]
SENSOR_NAMES = ["s1", "sensor_head"]
LINK_NAMES = ["r_wrist", "Head"]
ORIG_FILE = '/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig_sdf.sdf'
OUTPUT_FILE = '/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.sdf'

generateWholeSkin(verticesFiles=VERTICES,
                  sensorSizes=SENSOR_SIZES,
                  sensorNames=SENSOR_NAMES,
                  linkNames=LINK_NAMES,
                  origFile=ORIG_FILE,
                  outputFile=OUTPUT_FILE)