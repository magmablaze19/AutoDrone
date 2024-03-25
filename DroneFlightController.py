###################################################
#             Drone Flight Controller             #
#                                                 #
#       Author: Alex Longo                        #
#                                                 #
#         Date: 3/6/2024                          #
#                                                 #
#  Description: Main controller for conducting    #
#               communication with drone. Sends   #
#               and recieves data and provides    #
#               methods for doing so.             #
###################################################

# Required Imports
import socket
import threading
import time
import cv2




###############################################################
#      EVERYTHING BELOW THIS STILL NEEDS EDITING              #
###############################################################


class DroneFLightController:
    """  CLASS CONSTANTS  """
    ################################################################################
    TELLO_IP = '192.168.10.1'  # Tello IP address
    TELLO_PORT = 8889          # Tello port number

    LOCAL_IP = ''              # Local IP address
    LOCAL_PORT = 8889          # Local port number


    #################################################################################

    
    
    def __init__(self, record_log: bool=True, show_log: bool=True):

        
        # Opening local UDP port on 8889 for Drone communication
        self.local_ip = self.LOCAL_IP
        self.local_port = self.LOCAL_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.local_ip, self.local_port))
        
        # Setting Drone ip and port info
        self.tello_ip = self.TELLO_IP
        self.tello_port = self.TELLO_PORT
        self.tello_address = (self.tello_ip, self.tello_port)
        
        # Setting up potential query/response logging
        self.recording_log = record_log
        self.printing_log = show_log
        self.log = []

        # Intializing response thread
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # easyTello runtime options
        self.stream_state = False
        self.last_frame = None
        self.MAX_TIME_OUT = 15.0
        self.debug = debug
        # Setting Tello to command mode
        self.command()

    def send_command(self, command: str, query: bool =False):
        # Log command if necessary
        if (self.recording_log):
            self.log.append("")
        
        # New log entry created for the outbound command
        #self.log.append("Kaboom")

        # Sending command to Tello
        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        # Displaying conformation message (if 'debug' os True)
        #if self.debug is True:
        #    print('Sending command: {}'.format(command))
            
        # Checking whether the command has timed out or not (based on value in 'MAX_TIME_OUT')
        # start = time.time()
        # while not self.log[-1].got_response():  # Runs while no repsonse has been received in log
        #     now = time.time()
        #     difference = now - start
        #     if difference > self.MAX_TIME_OUT:
        #         print('Connection timed out!')
        #         break
        # Prints out Tello response (if 'debug' is True)
        #if self.debug is True and query is False:
            #print('Response: {}'.format(self.log[-1].get_response()))

    def _receive_thread(self):
        while True:
            # Checking for Tello response, throws socket error
            try:
                self.response, ip = self.socket.recvfrom(1024)
                self.log[-1].add_response(self.response)
            except socket.error as exc:
                print('Socket error: {}'.format(exc))

    def _video_thread(self):
        # Creating stream capture object
        cap = cv2.VideoCapture('udp://'+self.tello_ip+':11111')
        # Runs while 'stream_state' is True
        while self.stream_state:
            ret, self.last_frame = cap.read()
            cv2.imshow('DJI Tello', self.last_frame)

            # Video Stream is closed if escape key is pressed
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
    
    def wait(self, delay: float):
        # Displaying wait message (if 'debug' is True)
        if self.debug is True:
            print('Waiting {} seconds...'.format(delay))
        # Log entry for delay added
        self.log.append("Wait")
        # Delay is activated
        time.sleep(delay)
    
    def get_log(self):
        return self.log
    
    def close(self):
        self.socket.close()



    """ CONTROL COMMANDS """
    def command(self):
        self.send_command('command')
    
    def takeoff(self):
        self.send_command('takeoff')

    def land(self):
        self.send_command('land')

    def streamon(self):
        self.send_command('streamon')
        self.stream_state = True
        self.video_thread = threading.Thread(target=self._video_thread)
        self.video_thread.daemon = True
        self.video_thread.start()

    def streamoff(self):
        self.stream_state = False
        self.send_command('streamoff')

    def emergency(self):
        self.send_command('emergency')
    


    """ LOG COMMANDS """

