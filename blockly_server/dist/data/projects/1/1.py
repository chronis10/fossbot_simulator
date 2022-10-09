import time
import sys
import os
import inspect
import signal

from fossbot_lib.parameters_parser.parser import load_parameters
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.common.interfaces import robot_interface
from fossbot_lib.coppeliasim_robot.fossbot import FossBot as SimuFossBot

APP_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.dirname(os.path.dirname(APP_DIR))
CONF_DIR = os.path.join(DATA_DIR,'admin_parameters.yaml')




def custom():
  robot.rgb_set_color('red')
  while True:
    robot.move_forward()
    if robot.check_for_obstacle():
      robot.rotate_clockwise_90()




if __name__ == "__main__":
  
  
  FILE_PARAM = load_parameters(path=CONF_DIR)

  # Simulation robot test ===========================================
  SIM_IDS = configuration.SimRobotIds(**FILE_PARAM["simulator_ids"])
  SIM_PARAM = configuration.SimRobotParameters(
        sensor_distance=configuration.SensorDistance(**FILE_PARAM["sensor_distance"]),
        motor_left_speed=configuration.MotorLeftSpeed(**FILE_PARAM["motor_left"]),
        motor_right_speed=configuration.MotorRightSpeed(**FILE_PARAM["motor_right"]),
        default_step=configuration.DefaultStep(**FILE_PARAM["step"]),
        light_sensor=configuration.LightSensor(**FILE_PARAM["light_sensor"]),
        line_sensor_left=configuration.LineSensorLeft(**FILE_PARAM["line_sensor_left"]),
        line_sensor_center=configuration.LineSensorCenter(**FILE_PARAM["line_sensor_center"]),
        line_sensor_right=configuration.LineSensorRight(**FILE_PARAM["line_sensor_right"]),
        rotate_90=configuration.Rotate90(**FILE_PARAM["rotate_90"]),
        simulation=SIM_IDS)
  print(SIM_PARAM)
  robot = SimuFossBot(parameters=SIM_PARAM)
  try:
    custom()
  except Exception as e:
    print('Error on code!')
    print(e)
  finally:
    print('Gpio clean!!')
    robot.exit()
  
