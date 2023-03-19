import paramiko
from tkinter import *
fields = ('Annual Rate', 'Number of Payments', 'Loan Principle', 'Monthly Payment', 'Remaining Loan')

class GUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("FOSSBot Remote SSH")
        self.start_gui()
        self.entries = {}
        self.report_window = None
        
        self.ssh_agent = None

    def start_gui(self):
        self.entries = self.makeform(self.root)
        self.report_window = Text(self.root)
        #self.report_window.config(state= "disabled")
        self.report_window.pack(side = LEFT, padx = 5, pady = 5)
        frame1 = Frame(self.root)
        frame2 = Frame(self.root)
        b1 = Button(frame1, text = 'Connect',command= self.connect)
        b1.pack(side = LEFT, padx = 5, pady = 5)
        b2 = Button(frame1, text='Status',command= self.status)
        b2.pack(side = LEFT, padx = 5, pady = 5)
        b6 = Button(frame1, text='Network',command= self.network)
        b6.pack(side = LEFT, padx = 5, pady = 5)
        b3 = Button(frame2, text='Start Service',command= self.start_service)
        b3.pack(side = LEFT, padx = 5, pady = 5)
        b4 = Button(frame2, text='Stop Service',command= self.stop_service)
        b4.pack(side = LEFT, padx = 5, pady = 5)
        b5 = Button(frame2, text='Update',command= self.update)
        b5.pack(side = LEFT, padx = 5, pady = 5)

        frame1.pack(side = TOP)
        frame2.pack(side = TOP)
        self.root.mainloop()

    def connect(self):
        host =self.entries['Host'].get()
        username =self.entries['Username'].get()
        password =self.entries['Password'].get()
        try:
            self.ssh_agent = System_Agent(host,username,password)
            self.print_result('Connected!')
            
        except Exception as e:
            self.print_result(e)

    def status(self):
        if self.ssh_agent is not None:
            result = self.ssh_agent.execute('docker ps')
            self.print_result(result)
            
    def network(self):
        if self.ssh_agent is not None:
            ip = self.ssh_agent.execute('hostname -I')
            hostname = self.ssh_agent.execute('hostname')
            self.print_result(f'IP: {ip} Hostname: {hostname}')

    def update(self):
        if self.ssh_agent is not None:
            self.stop_service()
            result = self.ssh_agent.execute('docker pull chronis10/fossbot_blockly_phy:latest')
            self.print_result(result)
            self.start_service()
            
    def start_service(self):
        if self.ssh_agent is not None:
            result = self.ssh_agent.execute('docker compose  -f docker-compose.yaml up -d')
            self.print_result(result)

    def stop_service(self):
        if self.ssh_agent is not None:
            result = self.ssh_agent.execute('docker compose  -f docker-compose.yaml down')
            self.print_result(result)

    def print_result(self,msg):
        self.report_window.delete(1.0,"end")
        self.report_window.insert(1.0, msg)
        
    def makeform(self,root):
        fields = ('Host','Username','Password')
        values = ('192.168.1.127','pi','raspberry')
        entries = {}
        for i,field in enumerate(fields):
            row = Frame(root)
            lab = Label(row, width=22, text=field+": ", anchor='w')
            ent = Entry(row)
            ent.insert(0,values[i])
            row.pack(side = TOP, fill = X, padx = 5 , pady = 5)
            lab.pack(side = LEFT)
            ent.pack(side = RIGHT, expand = YES, fill = X)
            entries[field] = ent
        return entries

        
class System_Agent:
    def __init__(self,host,username,password):
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(host, username=username, password=password)

    def execute(self,cmd):
        _stdin, _stdout,_stderr = self.client.exec_command(cmd)
        return _stdout.read().decode()

    def disconnect(self):
        self.client.close()

    def __del__(self):
        self.client.close()

if __name__ == "__main__":
    #myagent = System_Agent("192.168.1.127","pi","raspberry")
    my_gui = GUI()
