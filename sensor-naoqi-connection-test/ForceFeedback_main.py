'''
Main controller of robot motion with current-feedback collision detection. For tips how to use it
read description of ForceFeedbackExperiment.py.

Before starting experiment you could want to configure the controller. It can be done in the Defines section
of this file. Most important parameters are:
POS_FILE_NAME: this .txt file contains target robot configurations (every row is one configuration).
You can generate it eg. with our program contact_finder.py.
PORT: probably not that important... robot has got 9559 almost every time...
IP_ROBOT: important, can be determined by short-press of robot chest button
CURRENT_LIMIT: important setting of collision detector, this value (0.14) was hand-tuned to be safe.
Make it higher only when you know what you are doing!
ARM: important, effector name. "RArm" or "LArm".
RsafePosition_joint, LsafePosition_joint: these values were hand-tuned to be safe. No need to change them.
r_names, l_names: no need to change them. It is mapping of joint names to their respective coordinates.

Functions:
 ->saveDataset: function which saves timestamps of recorded events (collisions, movement starts)
 ->exploreJoints: function which takes list of joint coordinates and drives robot to them. Also
 				contains collision detector.
 ->runExploration: function which wraps exploreJoints for easier multithreaded usage
'''

from naoqi import ALProxy
import numpy as np
import motion
import time
from UDP_listener import SkinDriver

# Defines
POS_FILE_NAME = "R_collisions3_longerseq.txt"
PORT = 9559
IP_ROBOT = "127.0.0.1"
CURRENT_LIMIT = 0.13
ARM = "RArm"
RsafePosition_joint = [0.940384,-0.437232, -0.113558, 0.638186, 0.055182, 0.009481]
LsafePosition_joint = [0.585946, 0.134950, -0.311444, -0.245398, 0.045978, 0.050935]
r_names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
l_names = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll", "LWristYaw", "LHand"]
# End of defines section


if(ARM == "RArm"):
	SAFE_POSITION_JOINT = RsafePosition_joint
	NAMES = r_names

else:
	SAFE_POSITION_JOINT = LsafePosition_joint
	NAMES = l_names


def saveDataset(experimentName, collision_time_stamps, newMotionTimeStamps, current_times, currents):
	np.savetxt(experimentName + '_' + 'col_time_stamps.txt', np.array(collision_time_stamps))
	np.savetxt(experimentName + '_' + 'mot_time_stamps.txt', np.array(newMotionTimeStamps))

def exploreJoints(start_joint, toVisit_joints, jointNames, effectorName):
	'''
	:param start_joint: this is considered as a safe position. Robot will start and end here and also return here
	after collison.
	:param toVisit_joints: this is a list of arrays(every array=configuration to visit). Coordinate in array
	corresponds to jointNames
	:param jointNames: this is a list of names of joints driven to positions toVisit_joints
	:param effectorName: name of effector accoring to naoqi, in our case "Arms"
	'''
	print("Joint exploration thread running")
	newMotionStartTimeStamps = list()
	collisionTimeStamps = list()
	currentsInTime = list()
	currentTimes = list()
	fractionMaxSpeed = 0.1
	motionProxy = ALProxy("ALMotion", IP_ROBOT, PORT)
	memoryProxy = ALProxy("ALMemory", IP_ROBOT, PORT)
	ttsProxy = ALProxy("ALTextToSpeech", IP_ROBOT, PORT)
	ledsProxy = ALProxy("ALLeds", IP_ROBOT, PORT)

	s = SkinDriver()

	for joint in jointNames:
		motionProxy.setStiffnesses(joint, 0.8)
	# Monitor for a given time. If current exceeds some limit, stop movement and
	# return to safe position.
	for pos in toVisit_joints:
		# Start nonblocking movement
		print('Going to:')
		pos[0] = pos[0] + 0.5
		pos[-3] = pos[-3] + 0.5
		print(pos)
		motionProxy.setCollisionProtectionEnabled('Arms', True)
		motionProxy.setAngles(jointNames, start_joint, fractionMaxSpeed)
		time.sleep(1)
		motionProxy.setCollisionProtectionEnabled('Arms', False)
		newMotionStartTimeStamps.append(time.time())
		motionProxy.setAngles(jointNames, pos, fractionMaxSpeed)
		# Read currents in a loop and monitor for limits
		N = 100  # How many times the monitor will be engaged before movement is stopped
		fsamp = 20  # Frequency of limit checking... So a total time (in seconds) for a movement will be N/fsamp...
		while (N > 0):
			N = N - 1
			d = s.GetDataOnce(0.05)

	motionProxy.setCollisionProtectionEnabled('Arms', True)
	motionProxy.setAngles(jointNames, start_joint, fractionMaxSpeed)
	time.sleep(3)

def runExploration():
		'''
		This function is meant to be run in a thread in parallel with robot internal data logger and
		optionally Optoforce data logger. It is a kind of an extension for function exploreJoints, which
		implements motion control and collision detection and also reading file with preconfigured positions
		to explore.
		'''
		posToVisit_joint = np.loadtxt(POS_FILE_NAME, comments="#", delimiter=" ", unpack=False)
		if(ARM == "RArm"):
			posToVisit_joint[:, 3] = [x + 0.3 for x in posToVisit_joint[:, 3]]
		else:
			posToVisit_joint[:, 3] = [x - 0.3 for x in posToVisit_joint[:, 3]]
		posToVisit_joint = (posToVisit_joint[:, 0:6]).tolist()

		#names = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw", "RHand"]
		exploreJoints(start_joint=SAFE_POSITION_JOINT,
					  toVisit_joints=posToVisit_joint,
					  jointNames=NAMES,
					  effectorName='RArms')

runExploration()

"""
if __name__ == "__main__":
	try:
		pos_joint = np.loadtxt("RArm_cols_2.txt", comments="#", delimiter=" ", unpack=False)
		print(pos_joint)
		posToVisit_joint = (pos_joint[:, 0:6]).tolist()
		posToVisit_joint[:,3] = [x + 0.1 for x in posToVisit_joint[:,3]]

		exploreJoints(start_joint=RsafePosition_joint,
				toVisit_joints=posToVisit_joint,
				jointNames=NAMES,
				effectorName='RArms')

	except KeyboardInterrupt:
		print("User initiated program shutdown! Moving to safe position...")
		motionProxy = ALProxy("ALMotion", IP_ROBOT, PORT)
		motionProxy.setCollisionProtectionEnabled('Arms', True)
		motionProxy.setAngles(["RShoulderPitch", "RShoulderRoll", "RElbowYaw","RElbowRoll","RWristYaw","RHand"],
							  R_SAFE_POSITION,
							  fractionMaxSpeed)
"""
