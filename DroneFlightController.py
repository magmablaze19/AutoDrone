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
        self.last_known_command = "None"
        self.response = None
        self.received_response_to_cur_cmd = False
        self.last_known_response = None
        self.receive_thread = threading.Thread(target=self._receive_thread)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        # Runtime options 
        self.stream_state = False
        self.last_frame = None
        
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

        # Update last known command
        self.last_known_command = command
        
        # Checking whether the command has timed out or not (based on value in 'MAX_TIME_OUT')
        start = time.time()
        while not self.received_response_to_cur_cmd:  # Runs while no repsonse has been received in log
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
            #print("\nReceived response: " + self.logger.get_response() + " \n")
            processed_response = self.process_response()
            print("\nReceived response: " + processed_response + " \n")


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
                    # Set lastknown response
                    self.last_known_response = str(self.response)
                    # Set received response flag to true
                    self.received_response_to_cur_cmd = True
                    # Log response if logging
                    if(self.recording_log):
                        processed_response = self.process_response()
                        self.logger.log_response(processed_response)
            # Catch any socket errors
            except socket.error as exc:
                print('Socket error: {}'.format(exc))


    # Capture drone video
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
    

    # Pause commands for specified number of seconds
    def wait(self, delay: float):
        # Log event if necesary        
        if(self.recording_log):
            self.logger.log_command("Wait " + str(delay) + " seconds")
        
        # Display wait confirmation if necessary
        if(self.printing_log):
            print("Initiated wait " + str(delay) + " seconds")
        
        # Activate delay
        time.sleep(delay)
    

    # Return the CommandResponseLogger
    def get_log(self):
        return self.logger

    # Save the log file
    def save_log(self):
        self.logger.save_log()
    
    # Close the socket
    def close(self):
        self.socket.close()


    """ CONTROL COMMANDS """
    # Put the drone in command mode
    def command(self):
        self.send_command('command')
    
    # Initiate auto-takeoff
    def takeoff(self):
        self.send_command('takeoff')

    # Initiate auto-land
    def land(self):
        self.send_command('land')

    # Begin streaming video
    def streamon(self):
        self.send_command('streamon')
        self.stream_state = True
        self.video_thread = threading.Thread(target=self._video_thread)
        self.video_thread.daemon = True
        self.video_thread.start()

    # End streaming video
    def streamoff(self):
        self.stream_state = False
        self.send_command('streamoff')

    # Stop all motors immediately
    def emergency(self):
        self.send_command('emergency')


    """ DRONE MOVEMENT COMMANDS """
    # Fly up with dist cm (20-500)
    def up(self, dist: int):
        self.send_command("up " + str(dist))

    # Fly down with dist cm (20-500)
    def down(self, dist: int):
        self.send_command("down " + str(dist))

    # Fly left with dist cm (20-500)
    def left(self, dist: int):
        self.send_command("left " + str(dist))

    # Fly right with dist cm (20-500)
    def right(self, dist: int):
        self.send_command("right " + str(dist))
    
    # Fly forward with dist cm (20-500)
    def forward(self, dist: int):
        self.send_command("forward " + str(dist))

    # Fly back with dist cm (20-500)
    def back(self, dist: int):
        self.send_command("back " + str(dist))

    # Rotate degr degrees clockwise (1-3600)
    def cw(self, degr: int):
        self.send_command("cw " + str(degr))
    
    # Rotate degr degrees counter clockwise (1-3600)
    def ccw(self, degr: int):
        self.send_command("ccw " + str(degr))

    # Execute flip in direction (l, r, f, b)
    def flip(self, direc: str):
        self.send_command("flip " + direc)

    # Go to a coordinate at a specified speed. x: 20-500  y: 20-500  z: 20-500  speed: 10-100
    def go(self, x: int, y: int, z: int, speed: int):
        self.send_command("go " + str(x) + " " + str(y) + " " + str(z) + " " + str(speed))


    """ SET COMMANDS """
    # Set drone speed to speed cm/s (10-100)
    def set_speed(self, speed: int):
        self.send_command("speed " + str(speed))

    # Send RC control via four channels. a: left/right (-100~100)  b: forward/backward (-100~100)  c: up/down (-100~100)  d: yaw (-100~100)
    def rc_control(self, a: int, b: int, c: int, d: int):
        self.send_command("rc " + str(a) + " " + str(b) + " " + str(c) + " " + str(d))

    # Set Wifi SSID and password
    def set_wifi(self, ssid: str, password: str):
        self.send_command("wifi " + ssid + " " + password)
    

    """ READ COMMANDS """
    # Get current speed (cm/s)
    def get_speed(self):
        self.send_command('speed?', True)
        return str(self.last_known_response)

    # Get current battery percentage (0-100 %)
    def get_battery(self):
        self.send_command('battery?', True)
        return str(self.last_known_response)

    # Get current fly time (seconds) 
    def get_time(self):
        self.send_command('time?', True)
        return str(self.last_known_response)

    # Get height (cm) 
    def get_height(self):
        self.send_command('height?', True)
        return str(self.last_known_response)
    
    # Get temperature (℃) 
    def get_temp(self):
        self.send_command('temp?', True)
        return str(self.last_known_response)

    # Get IMU attitude data (pitch, roll, yaw)
    def get_attitude(self):
        self.send_command('attitude?', True)
        return self.attitude_response()

    # Get barometer value (m)
    def get_baro(self):
        self.send_command('baro?', True)
        return str(self.last_known_response)

    # Get IMU angular acceleration data (0.001g)
    def get_acceleration(self):
        self.send_command('acceleration?', True)
        return str(self.last_known_response)
    
    # Get distance value from TOF（cm）
    def get_tof(self):
        self.send_command('tof?', True)
        return str(self.last_known_response)

    # Get Wi-Fi SNR
    def get_wifi(self):
        self.send_command('wifi?', True)
        return str(self.last_known_response)
    

    """ PROCESS DRONE RESPONSES """
    # Correctly process response
    def process_response(self):
        if 'attitude?' in self.last_known_command:
            return str(self.attitude_response())
        elif 'acceleration?' in self.last_known_command:
            return str(self.acceleration_response())
        elif 'temp?' in self.last_known_command:
            return str(self.temp_response())
        elif 'baro?' in self.last_known_command or 'speed?' in self.last_known_command:
            return str(self.float_response(self.last_known_response))
        elif '?' not in self.last_known_command:
            return str(self.last_known_response)
        else:
            return str(self.int_response(self.last_known_response))
    
    # Process a numeric response
    def numeric_response(self, data: str):
        num_val = ''.join(i for i in data if i.isdigit() or i=='-' or i=='.')
        return num_val

    # Process an integer response
    def int_response(self, data: str):
        return int(self.numeric_response(data))

    # Process a float response
    def float_response(self, data: str):
        return float(self.numeric_response(data))
    
    # Process an attitude rsponse
    def attitude_response(self):
        raw_att = self.last_known_response.split(';')
        att_data = (self.int_response(raw_att[0]), self.int_response(raw_att[1]), self.int_response(raw_att[2]))
        return att_data
    
    # Process an acceleration response
    def acceleration_response(self):
        raw_acc = self.last_known_response.split(';')
        acc_data = (self.float_response(raw_acc[0]), self.float_response(raw_acc[1]), self.float_response(raw_acc[2]))
        return acc_data

    # Process a temperature response
    def temp_response(self):
        raw_temp = self.last_known_response.split('~')
        temp = (self.int_response(raw_temp[0]) + self.int_response(raw_temp[1]))/2
        return temp