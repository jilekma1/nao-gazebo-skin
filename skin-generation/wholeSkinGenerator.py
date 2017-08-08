"""
Simple higher-level script for covering Nao robot with taxels.
Copyright (C) 2017  Martin Jilek

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
