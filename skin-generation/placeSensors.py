import numpy as np
#import scipy as sp
import xml.etree.ElementTree as ET
import pywavefront

ROBOT_DESCRIPTION = "nao_orig.xacro"
LINK_TEMPLATE = "link_template.txt"
SENSOR_TEMPLATE = "sens_template.txt"
GENERATE_TO_FILE = "sensors.xacro"
SENSOR_PARENT = "r_wrist"
SENSOR_DESCRIPTION_SKELETON = "sensor_skeleton.txt"


def loadSurface(raw_path):
    raw = np.loadtxt(raw_path)
    raw = np.reshape(raw,(-1, 3))
    # for each column find unique indices
    raw = remove_duplicates(raw)
    return raw

def remove_duplicates(array_data, return_index=False, return_inverse=False):
    """Removes duplicate rows of a multi-dimensional array. Returns the
    array with the duplicates removed. If return_index is True, also
    returns the indices of array_data that result in the unique array.
    If return_inverse is True, also returns the indices of the unique
    array that can be used to reconstruct array_data.
    from: https://gist.github.com/jterrace/1337531"""
    unique_array_data, index_map, inverse_map = np.unique(
        array_data.view([('', array_data.dtype)] * \
                        array_data.shape[1]), return_index=True,
        return_inverse=True)

    unique_array_data = unique_array_data.view(
        array_data.dtype).reshape(-1, array_data.shape[1])

    # unique returns as int64, so cast back
    index_map = np.cast['uint32'](index_map)
    inverse_map = np.cast['uint32'](inverse_map)

    if return_index and return_inverse:
        return unique_array_data, index_map, inverse_map
    elif return_index:
        return unique_array_data, index_map
    elif return_inverse:
        return unique_array_data, inverse_map

    return unique_array_data

def generate_sensor_file(vertices):
    '''
    Generate XML file with sensors. It can be appended to the end of robot URDF.
    Each sensor is one link.
    :param vertices: numpy array Nx3 of vertices where the skin will be placed
    :return:
    '''
    with open(GENERATE_TO_FILE, "w+") as fid:
        print("File created")
    with open(SENSOR_DESCRIPTION_SKELETON, 'r') as skeleton:
        data_orig = skeleton.read()
    for i,vertex in enumerate(vertices):

        """data_modif = data_orig
        data_modif = data_modif.replace("SENSOR_DESCRIPTION", "Auto-generated sensor " + str(i))
        data_modif = data_modif.replace("SENSOR_LINK_NAME", "Sensor_" + str(i) + "_link")
        data_modif = data_modif.replace("COLLISION_NAME", "Sensor_" + str(i) + "_link_collision")
        data_modif = data_modif.replace("SENSOR_JOINT_NAME", "Sensor_" + str(i) + "_joint")
        data_modif = data_modif.replace("SENSOR_PARENT", SENSOR_PARENT)
        data_modif = data_modif.replace("SENSOR_NAME", "Sensor_" + str(i))"""

        data_modif = data_orig.replace("SENSOR_DESCRIPTION", "Auto-generated sensor " + str(i))
        data_modif = data_modif.replace("SENSOR_LINK_NAME", "Sensor_" + str(i) + "_link")
        data_modif = data_modif.replace("COLLISION_NAME", "Sensor_" + str(i) + "_link_collision")
        data_modif = data_modif.replace("SENSOR_JOINT_NAME", "Sensor_" + str(i) + "_joint")
        data_modif = data_modif.replace("SENSOR_PARENT", SENSOR_PARENT)
        data_modif = data_modif.replace("SENSOR_NAME", "Sensor_" + str(i))

        s = str(vertices[i, :])
        s = s[1:-1]
        data_modif = data_modif.replace("XYZ", s)

        with open(GENERATE_TO_FILE, "a+") as fid:
            fid.write(data_modif)

def generateSensor2(vertices, LINK="r_wrist", SENSOR_NAME = "Col_Sensor", origFile='/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig.xacro'):
    '''
    Modify XML Nao file. It inserts sensors into it. These sensors are put onto Nao LINK.
    :param vertices: numpy array Nx3 of vertices where the skin will be placed
    :return:
    '''
    with open(origFile, 'r') as fid:
        outXML = fid.read()
    for i, vertex in enumerate(vertices):
        index = outXML.find('<link name="' + LINK + '"' +  '>')
        with open(LINK_TEMPLATE, 'r') as fid:
            linkTemplate = fid.read()
        with open(SENSOR_TEMPLATE, 'r') as fid:
            sensorTemplate = fid.read()
        linkTemplate = linkTemplate.replace("SENSOR_XYZ", str(vertex)[1:-1])
        linkTemplate = linkTemplate.replace("COLLISION_NAME", LINK + '_collision_' + str(i))
        sensorTemplate = sensorTemplate.replace("COLLISION_NAME", LINK + '_collision' + str(i))
        sensorTemplate = sensorTemplate.replace("SENSOR_NAME", LINK + '_collision_sens_' + str(i))
        print(index)
        outXML = outXML[0:index+len('<link name="' + LINK + '"' +  '>')] + linkTemplate + outXML[index + len('<link name="' + LINK + '"' +  '>'):]
        indexRef = outXML.find('<gazebo reference="' + LINK + '"' + '>')
        print('<gazebo reference="' + LINK + '"' + '>')
        print(indexRef)
        outXML = outXML[0:indexRef + len('<gazebo reference="' + LINK + '"' + '>')] + sensorTemplate + outXML[indexRef + len('<gazebo reference="' + LINK + '"' + '>'):]

    with open('/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.xacro', 'w+') as fid:
        fid.write(outXML)

def generateSensor_asInICub(vertices, LINK="r_wrist", SENSOR_NAME = "Col_Sensor", origFile='/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig.xacro'):
    with open(origFile, 'r') as fid:
        outXML = fid.read()
    with open(SENSOR_TEMPLATE, 'r') as fid:
        sensorTemplate = fid.read()
    collisionBlock = ''
    for i, vertex in enumerate(vertices):
        index = outXML.find('<link name="' + LINK + '"' +  '>')
        with open(LINK_TEMPLATE, 'r') as fid:
            linkTemplate = fid.read()
        linkTemplate = linkTemplate.replace("SENSOR_XYZ", str(vertex)[1:-1])
        linkTemplate = linkTemplate.replace("COLLISION_NAME", LINK + '_collision_' + str(i))
        collisionBlock = collisionBlock + "\n<collision>" + LINK+ "_collision_" + str(i) + "</collision>"
        print(index)
        outXML = outXML[0:index+len('<link name="' + LINK + '"' +  '>')] + linkTemplate + outXML[index + len('<link name="' + LINK + '"' + '>'):]
        indexRef = outXML.find('<gazebo reference="' + LINK + '"' + '>')
        print('<gazebo reference="' + LINK + '"' + '>')
        print(indexRef)
    sensorTemplate = sensorTemplate.replace("COLLISION_NAME", collisionBlock)
    sensorTemplate = sensorTemplate.replace("SENSOR_NAME", LINK + '_collision_sens')
    outXML = outXML[0:indexRef + len('<gazebo reference="' + LINK + '"' + '>')] + sensorTemplate + outXML[indexRef + len('<gazebo reference="' + LINK + '"' + '>'):]

    with open('/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.xacro', 'w+') as fid:
        fid.write(outXML)


def generatePolylineSensors(vertices,
                            LINK="torso",
                            SENSOR_NAME = "Col_Sensor",
                            origFile='/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig.xacro',
                            LINK_TEMPLATE = "/home/x200/Documents/Skola/NewNao/code-nao-simulation/skin-generation/polyline_link_template.txt"):
    # define path of a polyline - vertices on a one line = whole quad
    #vertices = np.reshape(vertices, (-1, 4))
    with open(origFile, 'r') as fid:
        outXML = fid.read()
    with open(SENSOR_TEMPLATE, 'r') as fid:
        sensorTemplate = fid.read()
    collisionBlock = ''

    """
    geometry = '<polyline>'
    for i, vertex in enumerate(vertices):
        geometry = geometry + "<point>" + str(vertex)[1:-1] + "</point>"
    geometry = geometry + "<height>0.1</height>"
    geometry = geometry + "</polyline>"
    """

    for i, vertex in enumerate(vertices):
        index = outXML.find('<link name="' + LINK + '"' +  '>')
        with open(LINK_TEMPLATE, 'r') as fid:
            linkTemplate = fid.read()
        center = np.mean(np.reshape(vertex, (-1, 3)), 0)
        center[0] = center[0] + 1
        linkTemplate = linkTemplate.replace("SENSOR_XYZ", str(center)[1:-1])
        linkTemplate = linkTemplate.replace("COLLISION_NAME", LINK + '_collision_' + str(i))

        geometry = '<box size="0.001 0.001 0.001"/>'
        """
        for j in range(len(vertex)/3):
            geometry = geometry + "<point>" + str(vertex[j:j+3])[1:-1] + "</point>"
        geometry = geometry + "<height>0.1</height>"
        geometry = geometry + "</box>"
        """

        linkTemplate = linkTemplate.replace("GEOMETRY_VISUAL", geometry)
        linkTemplate = linkTemplate.replace("GEOMETRY_COLLISION", geometry)
        collisionBlock = collisionBlock + "\n<collision>" + LINK+ "_collision_" + str(i) + "</collision>"
        #print(index)
        outXML = outXML[0:index+len('<link name="' + LINK + '"' +  '>')] + linkTemplate + outXML[index + len('<link name="' + LINK + '"' + '>'):]
        indexRef = outXML.find('<gazebo reference="' + LINK + '"' + '>')
        #print('<gazebo reference="' + LINK + '"' + '>')
        #print(indexRef)
    sensorTemplate = sensorTemplate.replace("COLLISION_NAME", collisionBlock)
    sensorTemplate = sensorTemplate.replace("SENSOR_NAME", LINK + '_collision_sens')
    outXML = outXML[0:indexRef + len('<gazebo reference="' + LINK + '"' + '>')] + sensorTemplate + outXML[indexRef + len('<gazebo reference="' + LINK + '"' + '>'):]

    with open('/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.xacro', 'w+') as fid:
        fid.write(outXML)


verts = loadSurface("nao-rwrist-coords.raw")
#generate_sensor_file(verts)
#generateSensor_asInICub(10*verts)
verts = np.loadtxt("torso_skin.raw")
print(verts)
verts = verts[0::2, :]
generatePolylineSensors(verts)
