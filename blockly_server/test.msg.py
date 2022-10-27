import socketio
import sys
 

sio = socketio.Client()

class Logger:
 
    def __init__(self,sio):
        self.console = sys.stdout
        self.sio = sio
        self.sio.connect('http://127.0.0.1:8080')
 
    def write(self, message):
        self.console.write(message)
        
        if len(message.strip()) > 0:
            self.sio.emit('terminal_msgs', {'data': message.strip()})
 
    def flush(self):
        self.console.flush()

@sio.event
def connect():
    print("I'm connected!")

@sio.event
def connect_error(data):
    print("The connection failed!")

@sio.event
def disconnect():
    print("I'm disconnected!")
    


sys.stdout = Logger(sio)
for i in range(0,100):
    print('Hello, World')
