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

def calcRPY(vec1, vec2):
    vd = vec2
    x = vd[0]
    y = vd[1]
    z = vd[2]
    #yaw = np.arctan(vd[0]/-vd[2])
    #pitch = np.arctan(np.sqrt(vd[0]**2 + vd[1]**2)/vd[2])
    #roll = np.arctan(vd[1]/vd[0])
    #yaw = np.arctan2(y, x)
    #l = np.sqrt(x*x + y*y)
    #pitch = np.arctan2(z, l)

    roll = np.arctan2(z, y) + 3.14/2
    pitch = 0
    l = np.sqrt(y*y + z*z)
    u = np.sqrt(x*x + y*y + z*z)
    yaw = (3.14/2)+np.arcsin(l/u)
    #yaw = 0

    yaw = np.arctan2(x, (-y)) + 3.14/2
    pitch = -np.arctan2(np.sqrt(x*x + y*y), z)


    #yaw = np.arctan2(x, z)
    #pitch = np.arctan2(l, y)

    #pitch = asin(-vec);
    #yaw = atan2(d.X, d.Z)
    return np.array([0, pitch, yaw])

def calcNormal(vertices):
    '''
    :param vertices: m * 3 array of m points
    :return: surface normal
    '''
    vertices = np.reshape(vertices, (-1, 3))
    a = vertices[1,:] - vertices[0, :]
    b = vertices[2,:] - vertices[0, :]
    return np.cross(a,b)

def generateIntoSDF(vertices,
                    LINK="r_wrist",
                    SENSOR_NAME = "Col_Sensor",
                    origFile='/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig_sdf.sdf',
                    outputFile = '/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao.sdf',
                    LINK_TEMPLATE = "/home/x200/Documents/Skola/NewNao/code-nao-simulation/skin-generation/sdf_link_template.txt",
                    SENSOR_TEMPLATE="sens_template.txt",
                    SENSOR_SIZE = '0.005 0.003 0.001'):
    '''
    This function generates skin from set of vertices. It takes an array of quads (each line is one quad) and places box
    sensors into their centers.
    :param vertices: m * 12 array of m quads
    :param LINK: link name to be covered with skin
    :param SENSOR_NAME: name of contact sensor
    :param origFile: file with original nao SDF
    :param LINK_TEMPLATE: template of a link
    :param SENSOR_TEMPLATE: template of a sensor
    :return:
    '''
    # define path of a polyline - vertices on a one line = whole quad
    #vertices = np.reshape(vertices, (-1, 4))
    with open(origFile, 'r') as fid:
        outXML = fid.read()
    with open(SENSOR_TEMPLATE, 'r') as fid:
        sensorTemplate = fid.read()
    collisionBlock = ''



    for i, vertex in enumerate(vertices):
        index = outXML.find("<link name='" + LINK + "'>")

        with open(LINK_TEMPLATE, 'r') as fid:
            linkTemplate = fid.read()
        center = np.mean(np.reshape(vertex, (-1, 3)), 0)

        normal = calcNormal(vertex)

        rpy = calcRPY(np.array([0,0,1]), normal)
        #print(rpy)

        pose = '<pose>' + str(center)[1:-1] + str(rpy)[1:-1] + '</pose>'

        linkTemplate = linkTemplate.replace("POSE", pose)
        linkTemplate = linkTemplate.replace("COLLISION_NAME", LINK + '_collision_' + str(i))

        geometry = '<box> <size>'+ SENSOR_SIZE + '</size></box>'

        linkTemplate = linkTemplate.replace("GEOMETRY_VISUAL", geometry)
        linkTemplate = linkTemplate.replace("GEOMETRY_COLLISION", geometry)
        collisionBlock = collisionBlock + "\n<collision>" + LINK+ "_collision_" + str(i) + "</collision>"
        outXML = outXML[0:index+len('<link name="' + LINK + '"' +  '>')] + linkTemplate + outXML[index + len('<link name="' + LINK + '"' + '>'):]
    indexRef = outXML.find("<link name='" + LINK + "'>")
    #indexRef = outXML.find("<model name='nao'>")
    sensorTemplate = sensorTemplate.replace("COLLISION_NAME", collisionBlock)
    sensorTemplate = sensorTemplate.replace("SENSOR_NAME", LINK + '_collision_sens')
    outXML = outXML[0:indexRef + len('<link name="' + LINK + '"' +  '>')] + sensorTemplate + outXML[indexRef + len('<link name="' + LINK + '"' +  '>'):]
    #indexRef = outXML.find("<link name='" + LINK + "'>")
    #outXML = outXML[0:indexRef + len('<link name="' + LINK + '"' + '>')] + "<self_collide>true</self_collide>" + outXML[
    #                                                                                                             indexRef + len(
    #                                                                                                                 '<link name="' + LINK + '"' + '>'):]
    #outXML = outXML[0:indexRef + len("<model name='nao'>")] + '<plugin name="model_push" filename="libcontact_model_plugin.so"/>' + outXML[indexRef + len("<model name='nao'>"):]
    print(i)

    with open(outputFile, 'w+') as fid:
        fid.write(outXML)


#def generateWholeSkin(vertices)

def generateWholeSkin(verticesFiles, sensorSizes, sensorNames, linkNames, origFile, outputFile):
    for i, file in enumerate(verticesFiles):
        if i>0:
            origFile = outputFile
        verts = np.loadtxt(file)
        generateIntoSDF(verts,
                        LINK = linkNames[i],
                        SENSOR_NAME=sensorNames[i],
                        SENSOR_SIZE=sensorSizes[i],
                        origFile = origFile,
                        outputFile = outputFile)
        print(i)


#verts = loadSurface("nao-rwrist-coords.raw")
#generate_sensor_file(verts)
#generateSensor_asInICub(10*verts)
#verts = np.loadtxt("rArm_skin.raw")
#verts = np.loadtxt("torso_skin.raw")
#generateIntoSDF(verts)

#generateIntoSDF(verts, LINK='torso_link',
#                SENSOR_NAME="Col_Sensor",
#                origFile='/home/x200/catkin_ws/src/nao_gazebo/gazebo_naoqi_control/models/nao_orig_sdf.sdf',
#                LINK_TEMPLATE="/home/x200/Documents/Skola/NewNao/code-nao-simulation/skin-generation/sdf_link_template.txt",
#                SENSOR_TEMPLATE="sens_template.txt")
