import time
import sys
import os
import inspect
import socketio
from fossbot_lib.parameters_parser.parser import load_parameters
from fossbot_lib.common.data_structures import configuration
from fossbot_lib.common.interfaces import robot_interface

ROBOT_MODE  = 'coppelia'
if os.getenv('ROBOT_MODE') is not None:
    if os.getenv('ROBOT_MODE') == 'physical':
        ROBOT_MODE = 'physical'


if ROBOT_MODE == 'physical':
    from fossbot_lib.real_robot.fossbot import FossBot
else:
    from fossbot_lib.coppeliasim_robot.fossbot import FossBot


DOCKER = False
if os.getenv('DOCKER') is not None:
    if os.getenv('DOCKER') == 'True':
        DOCKER = True


class Communication():
    def __init__(self, host='127.0.0.1', port= 8081 ,namespace='/test'):
        self.namespace = namespace
        self.sio = socketio.Client()
        self.sio.connect(f'http://{host}:{port}')
        self.start_event_handlers()

    def start_event_handlers(self):
        self.sio.on('connect', self.connect, namespace=self.namespace)
        self.sio.on('connect_error', self.connect_error, namespace=self.namespace)
        self.sio.on('disconnect', self.disconnect, namespace=self.namespace)

    def transmit(self,message):
        self.sio.emit('terminal_msgs', {'data': message})
    
    def connect(self):
        print("I'm connected!")

    def connect_error(self,data):
        print("The connection failed!")

    def disconnect(self):
        print("I'm disconnected!")

 
class Agent():
    def __init__(self):
        #APP_DIR = os.path.abspath(os.path.dirname(__file__))
        if DOCKER:
            BASED_DIR = '/app'
        else:
            BASED_DIR = os.path.abspath(os.path.dirname(sys.executable)) 

        DATA_DIR =  os.path.join(BASED_DIR,'data')
        CONF_DIR = os.path.join(DATA_DIR,'admin_parameters.yaml')
        FILE_PARAM = load_parameters(path=CONF_DIR)
        if ROBOT_MODE=='coppelia':  
            SIM_IDS = configuration.SimRobotIds(**FILE_PARAM["simulator_ids"])
            self.parameters = configuration.SimRobotParameters(
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
        else:
            self.parameters = configuration.RobotParameters(
            sensor_distance=configuration.SensorDistance(**FILE_PARAM["sensor_distance"]),
            motor_left_speed=configuration.MotorLeftSpeed(**FILE_PARAM["motor_left"]),
            motor_right_speed=configuration.MotorRightSpeed(**FILE_PARAM["motor_right"]),
            default_step=configuration.DefaultStep(**FILE_PARAM["step"]),
            light_sensor=configuration.LightSensor(**FILE_PARAM["light_sensor"]),
            line_sensor_left=configuration.LineSensorLeft(**FILE_PARAM["line_sensor_left"]),
            line_sensor_center=configuration.LineSensorCenter(**FILE_PARAM["line_sensor_center"]),
            line_sensor_right=configuration.LineSensorRight(**FILE_PARAM["line_sensor_right"]),
            rotate_90=configuration.Rotate90(**FILE_PARAM["rotate_90"]))
        
    def execute(self,code):
        robot = FossBot(parameters=self.parameters)
        coms = Communication()
        transmit = coms.transmit
        exec(code)
        
        robot.exit()
    
    def stop(self):
        pass
     

if __name__ == '__main__':
    a = Agent()
    a.execute('print("hello")')
    a.reset()
    


