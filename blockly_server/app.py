from flask import Flask,jsonify,request,Response, render_template,redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy_serializer import SerializerMixin
from jinja2 import Environment, FileSystemLoader
import subprocess
import os,signal
#import redis
import time
import psutil
import textwrap
import shutil
import yaml
from flask_socketio import SocketIO, emit
import glob
import json
import sys
import webbrowser
from xml.dom import minidom
import io
from robot.roboclass import Agent
from multiprocessing import Process,freeze_support
from threading import Thread
from flask_babel import Babel

from utils.systray_mode import systray_agent

DEBUG = os.getenv('DEBUG')
if DEBUG is None:
    DEBUG = False

SCRIPT_PROCCESS = None
COPPELIA_PROCESS = None
CURRENT_STAGE = None
app = Flask(__name__)
APP_DIR = os.path.abspath(os.path.dirname(__file__))
BASED_DIR = os.path.abspath(os.path.dirname(sys.executable)) 
#BASED_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

DATA_DIR =  os.path.join(BASED_DIR,'data')
SQLITE_DIR = os.path.join(DATA_DIR,'robot_database.db')
PROJECT_DIR =os.path.join(DATA_DIR,'projects')
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + SQLITE_DIR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['BABEL_DEFAULT_LOCALE'] = 'el'
# app.config['LANGUAGES'] =  {
#     'en': 'English',
#     'el': 'Greek',
# }
babel = Babel(app)




CORS(app)

# integrates Flask-SocketIO with the Flask application
socketio = SocketIO(app)

#r = redis.Redis(host='redis_server')

db = SQLAlchemy(app)

agent = Agent()



class Projects(db.Model, SerializerMixin):
    project_id = db.Column('project_id', db.Integer, primary_key = True)
    title = db.Column(db.String(100))
    info = db.Column(db.String(500))
    def __init__(self, title,info):
        self.title = title
        self.info = info


def execute_blocks(code):
    #print('hello')
    agent.execute(code)

def stop_coppelia():
    agent.stop()

# def open_coppelia():
#     start_coppelia()

def start_coppelia(stage):
    
    try:
        agent.stop()
    except:
        pass
    # stage_path = f'"{stage}"'
    # coppelia_path = '"C:\\Program Files\\CoppeliaRobotics\\CoppeliaSimEdu\\coppeliaSim.exe"'
    # os.system(f'cmd /k  "{coppelia_path} -gGUIITEMS_0 -s -q {stage_path}" ')

    
@app.before_first_request
def before_first_request():

    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)
        os.mkdir(PROJECT_DIR)
    elif not os.path.exists(PROJECT_DIR):
        os.mkdir(PROJECT_DIR)    
    get_sound_effects()
    try:
        db.session.query(Projects)
    except:
        db.create_all()

        if len(db.session.query(Projects)) == 0:
            create_kindergarten_files()
    if not os.path.exists(os.path.join(DATA_DIR,'admin_parameters.yaml')):
        shutil.copy(os.path.join(APP_DIR,'utils/code_templates/admin_parameters.yaml'),os.path.join(DATA_DIR,'admin_parameters.yaml'))

def create_kindergarten_files():
    title = "Kindergarten Project"
    info = "Default file for Kindergarten"
    project = Projects(title,info)
    db.session.add(project) 
    db.session.commit()
    db.session.refresh(project)
    os.mkdir(os.path.join(PROJECT_DIR,f'{project.project_id}'))
    shutil.copy(os.path.join(APP_DIR,'utils/code_templates/template.xml'),os.path.join(PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'))


@socketio.on('connection')
def on_connect(data):
    print("Socket connected, data received:", data)

@socketio.on('disconnection')
def on_disconnect(data):
    print("Socket disconnected!!, data received:", data)

@socketio.on_error()        # Handles the default namespace
def error_handler(e):
    print('Error - socket IO : ', e)

@app.route('/')
def index():
    
    stop_now()
    robot_name = get_robot_name()
    return render_template('home-page.html', robot_name=robot_name)

@socketio.on('get-all-projects')
def handle_get_all_projects():
    projects_list = get_all_projects()
    print('getting all projects')
    print(projects_list)

    emit('all-projects', { 'status': '200', 'data': projects_list})

@app.route('/blockly')
def blockly():
    stop_now()
    id = request.args.get('id') 
    print("------------------>",id)
    robot_name = get_robot_name()
    get_sound_effects()
    scenes = get_scenes()
    locale = app.config['BABEL_DEFAULT_LOCALE']
    return render_template('blockly.html', project_id=id, robot_name=robot_name,locale=locale,scenes=scenes)           

# @app.route('/test_terminal')
# def test_terminal():
#     socketio.emit('trm',  {'status': 'dokimh'}) 
#     return { 'status': '200'}

@app.route('/kindergarten')
def kindergarten():
    stop_now()
    robot_name = get_robot_name()
    scenes = get_scenes()
    # get_sound_effects()
    return render_template('blockly_simple.html', project_id=1, robot_name=robot_name,scenes=scenes)  

@socketio.on('get_sound_effects')
def blockly_get_sound_effects():
    if os.path.exists(os.path.join(DATA_DIR,'sound_effects.json')):
        with open(os.path.join(DATA_DIR,'sound_effects.json'), 'r') as file:
            sounds = json.load(file)
            emit('sound_effects',  { 'status': 200, 'data': sounds })
    else:
        emit('sound_effects', { 'status': 404, 'data': 'file does not exist'})       

@app.route('/admin_panel')
def admin_panel():
    stop_now()
    robot_name = get_robot_name()
    return render_template('panel-page.html', robot_name=robot_name)

@socketio.on('get_admin_panel_parameters')
def handle_get_admin_panel_parameters():
    parameters = load_parameters()
    parameters.pop('simulator_ids')
    emit('parameters', { 'status': '200', 'parameters': parameters})

@socketio.on('save_parameters')
def handle_save_parameters(data):
    try:
        params_values = json.loads(data['parameters'])
        print(params_values)
        parameters = load_parameters()
        i = 0
        for key, value in parameters.items():
            print(key)
            if key == 'robot_name':                
                value['value'] = params_values['robot_name']
            elif key != 'simulator_ids':     
                value['value'] = int(params_values[key])
            i = i + 1

        save_parameters(parameters)
        emit('save_parameters_result', { 'status': '200', 'data': parameters})
    except Exception as e:
        print(e)
        emit('save_parameters_result', { 'status': 'error', 'data': 'parameters not saved'})

@socketio.on('projects')
def handle_projects():
    projects_list = get_all_projects()
    data = jsonify(projects_list)
    emit('projects', { 'status': '200', 'data': data })

@socketio.on('new_project')
def handle_new_project(data):
    title = data['title']
    info = data['info']
    project = Projects(title,info)
    db.session.add(project)
    db.session.commit()
    db.session.refresh(project)
    os.mkdir(os.path.join(PROJECT_DIR,f'{project.project_id}'))
    shutil.copy(os.path.join(APP_DIR,'utils/code_templates/template.xml'),os.path.join(PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'))
    emit('new_project_result', { 'status': '200', 'project_id': project.project_id }) 

@socketio.on('delete_project')
def handle_delete_project(data):
    try:
        project_id = data['project_id']
        project = Projects.query.get(project_id)
        print(type(project))
        db.session.delete(project)
        db.session.commit()
        shutil.rmtree(os.path.join(PROJECT_DIR,f'{project.project_id}'))
        emit('delete_project_result', {'status':'200', 'project_deleted': 'true' })
    except Exception as e:
        print(e)
        emit('delete_project_result', {'status':'error', 'project_deleted': 'false'})

@socketio.on('edit_project')
def handle_edit_project(project_id):
    try:
        project = Projects.query.get(project_id)
        project.title = request.args.get('title')    
        project.info = request.args.get('info')
        db.session.commit()       
        emit('edit_project', {'status':'updated'})
    except Exception as e:
        print(e)
        emit('edit_project', {'status':'error'})

@socketio.on('execute_script')
def handle_execute_script(data):
    id = data['project_id']
    result = execute_code(id)
    emit('execute_script_result', result)

@socketio.on('script_status')
def handle_script_status():
    global SCRIPT_PROCCESS
    if SCRIPT_PROCCESS is None or SCRIPT_PROCCESS.poll() is not None:       
        emit('script_status',  {'status': 'completed'}) 
    else:
        emit('script_status',  {'status': 'still running'}) 

@app.route('/stop_script')
def stop_script():
    result = stop_now()
    return jsonify(result)

@socketio.on('stop_script')
def handle_stop_script():
    result = stop_now()
    emit('stop_script', result)

@socketio.on('manual_control_command')
def handle_manual_control_command(data):
   try:
     command = data['command']
     print(f'flask {command}')
     r.set('command',bytes(command, "utf8"))
     r.expire('command', 2)
     emit('manual_control_command_result',  {'status': '200', 'command received and executed': command})
   except Exception as e:
     print(e)
     emit('manual_control_command_result',  {'status': 'error', 'e': e})

@app.route('/manual_control')
def manual_control():
    stop_script()
    execute_code(None,manual_control=True)
    robot_name = get_robot_name()
    return render_template('control.html', robot_name=robot_name)

@socketio.on('manual_control')
def handle_manual_control():
   stop_script()
   execute_code(None,manual_control=True)
   emit('manual_control',  {'status': 'ok'})

@socketio.on('terminal_msgs')
def handle_terminal_msgs(data):
    print(data)
    socketio.emit('trm',  data)

@socketio.on('testmsg')
def test_msgs(data):
    print('test')
    #socketio.emit('trm',  data)




@socketio.on('execute_blockly')
def handle_execute_blockly(data):
    global SCRIPT_PROCCESS
    socketio.emit('execute_blockly_robot', {'status': '200', 'result': 'Code saved with success'})
    try:
        id = data['id']
        code = data['code']
        print(code)
        try:
            stop_script()
            #SCRIPT_PROCCESS = threading.Thread(target=execute_blocks, args=(code,))
            SCRIPT_PROCCESS = Process(target=execute_blocks, args=(code,),daemon=True)
            SCRIPT_PROCCESS.start()
        except Exception as e:
            print(e)
        #print(SCRIPT_PROCCESS)
        #generate_py(code,id)
        
        #result = execute_code(id)  
        #emit('execute_blockly_result', result)
        emit('execute_blockly_result', {'status': '200'})
    except Exception as e:
        print(e)
        emit('execute_blockly_result',  {'status': 'error when creating .py file or when running the .py file'})



@socketio.on('open_map')
def open_map(data):
    global CURRENT_STAGE,COPPELIA_PROCESS
    files = glob.glob(os.path.join(DATA_DIR,f'Coppelia_Scenes/{data}')) 
    if ".ttt" in files[0]:
        CURRENT_STAGE = files[0]
        reset_coppelia()
        emit('execute_blockly_result', {'status': '200'})


@socketio.on('open_audio_folder')
def open_audio_folder():
    os.startfile(os.path.realpath(os.path.join(DATA_DIR,'sound_effects')))


@socketio.on('open_stage_folder')
def open_map_folder():
    os.startfile(os.path.realpath(os.path.join(DATA_DIR,'Coppelia_Scenes')))

@socketio.on('reset_stage')
def reset_coppelia():
    global COPPELIA_PROCESS,CURRENT_STAGE
    if COPPELIA_PROCESS is not None:
        COPPELIA_PROCESS.terminate()
    COPPELIA_PROCESS = Process(target=start_coppelia,args=(CURRENT_STAGE,),daemon=False)
    COPPELIA_PROCESS.start()
    #emit('execute_blockly_result', {'status': '200'})



@socketio.on('send_xml')
def handle_send_xml(data):
    try:
        id = data['id']
        with open (os.path.join(PROJECT_DIR,f'{id}/{id}.xml'), "r", encoding="utf8") as myfile:
            data=myfile.readlines()
        emit('send_xml_result', {'status': '200', 'data': data})   
    except Exception as e:
        emit('send_xml_result',  {'status': 'file not found'})

@socketio.on('save_xml')
def handle_save_xml(data):
    try: 
        id = data['id']
        code = data['code']
        
        
        project = Projects.query.get(id)        
        
        
        code = code.replace('</xml>','')
        extra_info = ''.join(['  <project>\n', f'    <title>{project.title}</title>\n', f'    <description>{project.info}</description>\n', '  </project>\n', '</xml>'])
        code += extra_info
        
        with open(os.path.join(PROJECT_DIR,f'{id}/{id}.xml'), "w", encoding="utf8") as fh:
            fh.write(code)
        emit('save_xml_result', {'status': '200', 'result': 'Code saved with success'})
    except Exception as e:
       
        emit('save_xml_result',  {'status': 'error occured', 'result': 'Code was not saved'})

@app.route('/export_project/<int:id>')
def export_project(id):
    print(id)
    path = os.path.join(PROJECT_DIR,f'{id}/{id}.xml')
    return send_file(path, as_attachment=True)


@app.route('/upload_project', methods=[ 'POST'])
def upload_project():    
    if request.method == 'POST':
        if 'file' not in request.files:
            
            return redirect("/")
        file = request.files['file']
        if file.filename == '':
            
            return redirect("/")
        #in_memory_file = io.BytesIO()
        #file.save(in_memory_file)
        data = file.read().decode('utf-8')
        docs = minidom.parseString(data)
        pjs = docs.getElementsByTagName('project')[0]
        title = pjs.getElementsByTagName('title')[0].firstChild.data
        info = pjs.getElementsByTagName('description')[0].firstChild.data
        project = Projects(title,info)
        db.session.add(project)
        db.session.commit()
        db.session.refresh(project)        
        os.mkdir(os.path.join(PROJECT_DIR,f'{project.project_id}'))
        with open(os.path.join(PROJECT_DIR,f'{project.project_id}/{project.project_id}.xml'), "w", encoding="utf8") as fh:
            fh.write(data)
       
    return redirect("/")
    # print(id)
    # path = os.path.join(PROJECT_DIR,f'{id}/{id}.xml')
    # return send_file(path, as_attachment=True)

def get_all_projects():
    projects = Projects.query.all()
    projects_list = [pr.to_dict() for pr in projects]
    return projects_list


def generate_py(code,id):
    env = Environment(loader=FileSystemLoader(os.path.join(APP_DIR,'utils/code_templates')))
    template = env.get_template('template_code.py')
    code = textwrap.indent(text=code, prefix='  ', predicate=lambda line: True)
    output = template.render(code = code)
    with open(os.path.join(PROJECT_DIR,f'{id}/{id}.py'), "w" , encoding=('utf-8')) as fh:
        fh.write(output)

def execute_code(id,manual_control=False):
    global SCRIPT_PROCCESS
    my_env = os.environ.copy()
    if not manual_control:
        if not os.path.exists(os.path.join(PROJECT_DIR,f'{id}/{id}.py')):
            return {'status': 'file not found'}    
        if SCRIPT_PROCCESS is None or SCRIPT_PROCCESS.poll() is not None:        
            SCRIPT_PROCCESS = subprocess.Popen(['python', os.path.join(PROJECT_DIR,f'{id}/{id}.py')],env= my_env)
            return {'status': 'started'}
        else:
            return {'status': 'still running'}
    else:
        stop_now()
        SCRIPT_PROCCESS = subprocess.Popen(['python', os.path.join(APP_DIR,'utils/manual_control.py')])
        return {'status': 'started'}


def stop_now():
    global SCRIPT_PROCCESS
    print(SCRIPT_PROCCESS)
    print('stop')
    if SCRIPT_PROCCESS is None:
        return{'status': 'nothing running'}
    else:
        try:
            SCRIPT_PROCCESS.terminate()
            return {'status': 'stopped'}
        except Exception as e:
            print(e)
            return{'status': 'nothing running'}
    # if SCRIPT_PROCCESS is not None:   
    #     if sys.platform == 'win32':
    #         os.system("taskkill /F /pid "+str(SCRIPT_PROCCESS.pid))
    #     else:
    #         os.kill(SCRIPT_PROCCESS.pid, signal.SIGINT)

    #     SCRIPT_PROCCESS.terminate()
    #     print(SCRIPT_PROCCESS.poll())
    #     SCRIPT_PROCCESS = None
    #     print( 'stopped')
    #     return {'status': 'stopped'}
    # else:
    #     print( 'nothing running')
    #     return{'status': 'nothing running'}


# def stop_now():
#     global SCRIPT_PROCCESS
#     if SCRIPT_PROCCESS is not None:   
#         if sys.platform == 'win32':
#             os.system("taskkill /F /pid "+str(SCRIPT_PROCCESS.pid))
#         else:
#             os.kill(SCRIPT_PROCCESS.pid, signal.SIGINT)

#         SCRIPT_PROCCESS.terminate()
#         print(SCRIPT_PROCCESS.poll())
#         SCRIPT_PROCCESS = None
#         print( 'stopped')
#         return {'status': 'stopped'}
#     else:
#         print( 'nothing running')
#         return{'status': 'nothing running'}
        
def load_parameters():
    with open(os.path.join(DATA_DIR,'admin_parameters.yaml'), encoding=('utf-8')) as file:
        parameters = yaml.load(file, Loader=yaml.FullLoader)
    return parameters

def save_parameters(parameters):
    with open(os.path.join(DATA_DIR,'admin_parameters.yaml'), 'w', encoding=('utf-8')) as file:
        parameters = yaml.dump(parameters, file)

def get_robot_name():
    parameters = load_parameters()
    for key, value in parameters.items():
        if(key == "robot_name"):
            print("Getting robot name: ", value['value'] )
            return value['value']
    return " "

def get_scenes():
    files = glob.glob(os.path.join(DATA_DIR,'Coppelia_Scenes/*.ttt')) 
    names = [item.split("\\")[-1] for item in files]
    return names

def get_sound_effects():
    print("Getting sounds")    
    if os.path.exists(os.path.join(DATA_DIR,'sound_effects')):
        mp3_sounds_list = glob.glob(os.path.join(DATA_DIR,'sound_effects/*.mp3'))
        sounds_names = []
        for sound in mp3_sounds_list: 
            # split_list = sound.split("/")
            # audio_name = split_list[2] 
            split_list = os.path.split(sound)
            audio_name = split_list[-1]
            audio_name_list = audio_name.split(".")
            audio_name = audio_name_list[0]
            sounds_names.append({ "sound_name": audio_name, "sound_path": os.path.normpath(sound)})        
        print("sound effects:")        
        #delete first the json file if exists and then create it again 
        if os.path.exists(os.path.join(DATA_DIR,'sound_effects.json')):
            os.remove(os.path.join(DATA_DIR,'sound_effects.json'))
        with open(os.path.join(DATA_DIR,'sound_effects.json'), 'w') as out_file:
            json.dump(sounds_names, out_file)  


def shutdown_flask():
    from win32api import GenerateConsoleCtrlEvent
    CTRL_C_EVENT = 0
    GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0)

def imed_exit():
    try:
        # try to exit gracefully
       shutdown_flask()
    except Exception as e:
        # force quit
        os._exit(0)


@app.route("/shutdown")
def shutdown():
    imed_exit()
    

@socketio.on('systray_controls')
def handle_systray_controls(message):

    if message['data'] == 'exit':
        imed_exit()
    else:
        print(message)


if __name__ == '__main__':
    freeze_support()
    systray = Thread(target=systray_agent,daemon=True)
    systray.start()
    webbrowser.open_new("http://127.0.0.1:8081")
    socketio.run(app, host = '0.0.0.0',port=8081, debug=True)
