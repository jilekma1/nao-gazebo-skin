This repository contains a set of tools for NAO robot simulation:
__1) nao-gazebo-modified-for-G7__
This is basically nao-gazebo plugin (https://github.com/costashatz/nao_gazebo) modified to work with Gazebo 7 and ROS Indigo.
To use it, put it into your catkin workspace and compile it. 

For succesfull compilation on Ubuntu 14.04 (default for ROS Indigo), you might need at least gcc 4.9 (because of a c++ 11 features). You can have more versions of gcc with update-alternatives - try to look here: https://codeyarns.com/2015/02/26/how-to-switch-gcc-version-using-update-alternatives/

In fact you must install gcc/g++ 4.9 and pass it to update-alternatives like this:

    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.8 100 --slave /usr/bin/g++ g++ /usr/bin/g++-4.8

    sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-4.9 50 --slave /usr/bin/g++ g++ /usr/bin/g++-4.9

Then you can switch default compiler with:

    sudo update-alternatives --config gcc

Whole plugin schematics can be found here: https://github.com/martinj8649/nao-gazebo-skin/tree/master/docs/nao_gazebo_skin_schematics.png
    

__2) robot-models__
Here you can find nao robot models. All are based on nao-gazebo plugin model. There are .xacro files, which are not used by our project at this moment. Two files are important:
 -> nao_skin_hand_corrected.sdf : this file is what generates artificial skin generator, but skin segments placement is corrected by hand, but there is a problem that nao loses gravity when multiple self_collide tags are set to true
 -> nao_hand_corrected_no_gravity_bug.sdf : issue with self_collide tags is solved
 -> __nao_final.sdf : most recent and working model (27.7.2017)__, skin on r_wrist, l_wrist, Head and base_link.

__3) skin-generation__
Here you can find many files. For us, the important ones are:
-> link_template.txt: this is template, which will be modified by skin generator and inserted into link sdf description for each taxel
-> sens_template.txt: this is template of a skin sensor, again modified by generator and inserted
-> sensor_template.txt: template of a skin sensor, but used by older generator functions.
-> wholeSkinGenerator.py: code which calls placeSensors.py. In the code you can choose links of a robot to cover with skin, path to original nao sdf, path to output modified model and paths to files with vertices, which will be used to calculate taxel positions
-> placeSensors.py: called by wholeSkinGenerator, there are more functions, most of them 
are old and were used in first stages of development - focus on __generateIntoSDF()__ and __generateWholeSkin()__.

__4) sensor-naoqi-connection-test__
This is a complete setup of a contact experiment, where the robot tries to reach predefined collision (self-touch) configurations. Collisions are simply reported into the command line.
Just set variables POS_FILE_NAME to path to file with configurations in joint space and ARM ("LArm", "RArm"). Remember, for each hand joint space you need different coordinates! Arms are different...
NOTE: This experiment is slightly modified - positions were sampled with different Nao model, so in some positions robot is not able to touch itself, when it should. So to fourth joint here is added angle 0.3 rad (lines 116, 119).

__5) gazebo-skin plugin__
This is a Gazebo sensor plugin for our skin, which reads collision data and does some preprocessing. It contains UDP server, which publishes processed collision data on port 9091 (in form of strings).
