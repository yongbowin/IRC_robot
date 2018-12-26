import socket
import koji as brew
from operator import attrgetter
import re
 
 
class IRCBot:
    def __init__(self, **kwargs):
        self.settings = {
            'host':"xxx.xxx.xxx.xxx",
            'port':6667,
            'channel':"#nlp",
            'contact': ":",
            'nick':"redbot-rt",
            'ident':'redbot-rt',
            'realname':'redbot-rt'
        }
        self.add_kwargs(kwargs)
        self.sock = self.irc_conn()
        self.main_loop()
    def add_kwargs(self, kwargs):
        '''
        add keyword args as class attributes. 
        '''
        for kwarg in kwargs:
            if kwarg in self.settings:
                self.settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("{} has no keyword: {}".format(self.__class__.__name__, kwarg))
        self.__dict__.update(self.settings)
         
    def irc_conn(self):
        '''
        connect to server/port channel, send nick/user 
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('connecting to "{0}/{1}"'.format(self.host, self.port))
        sock.connect((self.host, self.port))
        print('sending NICK "{}"'.format(self.nick))
        sock.send("NICK {0}\r\n".format(self.nick).encode())
        sock.send("USER {0} {0} bla :{0}\r\n".format(
            self.ident, self.host, self.realname).encode())
        print('joining {}'.format(self.channel))
        sock.send(str.encode('JOIN '+self.channel+'\n'))
        return sock
         
    def main_loop(self):
        '''
        The main loop to keep the program running and waiting for commands
        '''
        while True:
            self.parse_data()
            self.ping_pong()
            self.check_command()
 
    def get_user(self, stringer):
        '''get username from data string'''
        start = stringer.find('~')
        end = stringer.find('@')
        user = stringer[start+1:end]
        return user
             
    def parse_data(self):
        '''
        get server data and parse it based on each message/command in irc
        '''
        data=self.sock.recv(1042) # recieve server messages
        data = data.decode('utf-8') # byte to str
        self.data = data.strip('\n\r')
        try:
            self.operation = data.split()[1] # get operation ie. JOIN/QUIT/PART/etc.
            textlist = data.split()[3:]
            text = ' '.join(textlist)
            self.text = text[1:] # content of each message
            self.addrname = self.get_user(data) # get address name
            self.username = data[:data.find('!')][1:] # get username
            self.cmd = self.text.split()[0][1:]
        except IndexError: # startup data has different layout than normal
            pass
             
    def ping_pong(self):
        '''
        The server pings and anything that does not pong back gets kicked
        '''
        try:
            if self.data[:4] == 'PING':
                self.send_operation('PONG')
        except TypeError: # startup data
            pass
             
    def send_operation(self, operation=None, msg=None, username=None):
        '''
        the specific string structure of sending an operation and private message to one user
        '''
        if msg is None:
            # send ping pong operation
            self.sock.send('{0} {1}\r\n'.format(operation, self.channel).encode())
        elif msg != None:
            # send private msg to one username
            self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.username, msg).encode())
             
    def say(self, string):
        '''
        send string to channel...the equivalent to print() in the IRC channel
        '''
        self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.channel, string).encode())
    
    def split_nvr(self, nvr):
        '''
        To split nvr for the purpose of competing
        '''
        return re.findall('\d+',nvr.split("-")[-1])

    def compete_nvr(self, a, b, flag):
        '''
        compete nvr to know the newer kernel-rt version 
        '''
        if not b:
            return True

        if flag == "y":
            if not (a.split("-")[-1].split(".")[0]).isdigit():
                return False
        elif flag == "z":
            if not ("".join(a.split("-")[-1].split(".")[:3])).isdigit():
                return False

        a_list = self.split_nvr(a)
        b_list = self.split_nvr(b)

        for i in range(len(a_list)):
            if int(a_list[i]) > int(b_list[i]):
                return True
            elif int(a_list[i]) < int(b_list[i]):
                return False
            else:
                continue

        return False

    def responseInfo(self, volumeID, pre_nvr=''):
        '''
        get package info, builds list, latest build ...
        '''
        hub = brew.ClientSession('http://brewhub.devel.redhat.com/brewhub')
        pkg_id = hub.getPackageID("kernel-rt")
        state = 1 # completed
        build_list = hub.listBuilds(pkg_id, state=state, volumeID=volumeID)
        
        latest_version_y = ''
        latest_version_z = ''
        for build in build_list:
            if pre_nvr == '':
                if build.has_key('nvr') and build['nvr'] and '+' not in build['nvr']:
                    if len((build['nvr']).split('.')) == 6 and self.compete_nvr(build['nvr'], latest_version_y, "y"):
                        build['nvr'].split('-')[-1].split('.')
                        latest_version_y = build['nvr']
                    elif len((build['nvr']).split('.')) == 8 and self.compete_nvr(build['nvr'], latest_version_z, "z"):
                        latest_version_z = build['nvr']
                    else:
                        continue
                else:
                    continue
            else:
                if build.has_key('nvr') and build['nvr'] and '+' not in build['nvr'] and (pre_nvr == ".".join(((build['nvr']).split("."))[:3])):
                    if len((build['nvr']).split('.')) == 6 and self.compete_nvr(build['nvr'], latest_version_y, "y"):
                        latest_version_y = build['nvr']
                    elif len((build['nvr']).split('.')) == 8 and self.compete_nvr(build['nvr'], latest_version_z, "z"):
                        latest_version_z = build['nvr']
                    else:
                        continue
                else:
                    continue
            
        if latest_version_y:
            string_y = self.username + ': Latest RT brew build [Y]: ' + latest_version_y
            string_z = self.username + ': Latest RT brew build [Z]: ' + latest_version_z
            self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.channel, string_y).encode())
            self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.channel, string_z).encode())
        else:
            string = self.username + ': Error'
            self.sock.send('PRIVMSG {0} :{1}\r\n'.format(self.channel, string).encode())

    def check_command(self):
        '''
        check each and every message for a command

        rhel-7 vplumeID=8
        rhel-8 volumeID=9
        '''
        if self.text[:1] == self.contact: # respond to only contact code to not respond to all messages
            if (self.cmd).lower() in ["rt", "rhel-rt", "rhel8"]:
                self.responseInfo(9)
            elif ((self.cmd)[:6]).replace("-", "").lower() == "rhel7":
                self.responseInfo(8)
            elif ((self.cmd)[:6]).replace("-", "").lower() == "rhel8":
                self.responseInfo(9)
            elif (len((self.cmd).split(".")) > 3):
                pre_nvr = (".".join(((self.cmd).split("."))[:3])).replace("kernel", "kernel-rt")
                if "kernel-3.10.0" in self.cmd:
                    self.responseInfo(8, pre_nvr)
                elif "kernel-4.18.0" in self.cmd:
                    self.responseInfo(9, pre_nvr)
                else:
                    self.say(self.cmd)
            else:
                self.say(self.cmd)
         
bot = IRCBot()
