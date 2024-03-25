###################################################
#             Drone Flight Controller             #
#                                                 #
#       Author: Alex Longo                        #
#                                                 #
#  Last Update: 3/25/2024                         #
#                                                 #
#  Description: Main flight controller for        #
#               sending commands to the drone and #
#               receiving responses from the      #
#               drone. Serves as an interface for #
#               the drone and provides methods    #
#               for interacting with it. Also     #
#               logs flight events using the      #
#               CommandResponseLogger.            # 
###################################################

# Required Imports
import socket
import threading
import time
import cv2
import CommandResponseLogger

class DroneFlightController:
    """  CLASS CONSTANTS  """
    # Tello IP address
    TELLO_IP = '192.168.10.1'  
    
    # Tello port number
    TELLO_PORT = 8889         

    # Local IP address
    LOCAL_IP = ''

    # Local port number              
    LOCAL_PORT = 8889          

    # Seconds until time out
    MAX_TIME_OUT = 15.0

    
    def __init__(self, record_log: bool=True, show_log: bool=True):

        
        # Open local UDP port on 8889 for Drone communication
        self.local_ip = self.LOCAL_IP
        self.local_port = self.LOCAL_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.local_ip, self.local_port))
        
        # Set Drone ip and port info
        self.tello_ip = self.TELLO_IP
        self.tello_port = self.TELLO_PORT
        self.tello_address = (self.tello_ip, self.tello_port)
        
        # Set up potential query/response logging
        self.recording_log = record_log
        self.printing_log = show_log
        self.logger = CommandResponseLogger.CommandResponseLogger()

        # Intialize response thread
        self.received_response_to_cur_cmd = False
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        """[START NEEDS EDITING]"""
        # Runtime options 
        self.stream_state = False
        self.last_frame = None
        self.MAX_TIME_OUT = 15.0
        """[END NEEDS EDITING]"""
        
        # Setting Tello to command mode
        self.command()


    # Send commands to drone
    def send_command(self, command: str, query: bool =False):
        # Re-initialize received_response variable
        self.received_response_to_cur_cmd = False
        
        # Log command if necessary
        if (self.recording_log):
            self.logger.log_command(command)
        # Display command confirmation if necessary
        if (self.printing_log):
            print("\nSending command: " + command + " \n")
            
        # Send command to Drone
        self.socket.sendto(command.encode('utf-8'), self.tello_address)
        
        # Checking whether the command has timed out or not (based on value in 'MAX_TIME_OUT')
        start = time.time()
        while not self.logger.got_response():  # Runs while no repsonse has been received in log
             now = time.time()
             difference = now - start
             if difference > self.MAX_TIME_OUT:
                 self.logger.log_time_out(True)
                 if (self.printing_log):
                    print('\nConnection timed out! \n')
                 break
             
        # Response logged if necessary by receive thread
        # Display response confirmation if necessary
        if (self.printing_log):
            print("\nReceived response: " + self.logger.get_response() + " \n")


    # Constantly check for drone responses
    def _receive_thread(self):
        while True:
            # Checking for Tello response, throws socket error
            try:
                # Empty old response field
                self.response = None
                # Try to grab a response
                self.response, ip = self.socket.recvfrom(1024)
                # Check if reponse was received
                if(self.response is None):
                    self.received_response_to_cur_cmd = False
                else:
                    # Log response if logging
                    if(self.recording_log):
                        self.logger.log_response(self.response)
                    # Set received response flag to true
                    self.received_response_to_cur_cmd = True
            # Catch any socket errors
            except socket.error as exc:
                print('Socket error: {}'.format(exc))


    ###############################################################
    #      EVERYTHING BELOW THIS STILL NEEDS EDITING              #
    ###############################################################


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
    