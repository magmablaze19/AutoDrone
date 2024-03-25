###################################################
#            Command / Response Logger            #
#                                                 #
#       Author: Alex Longo                        #
#                                                 #
#  Last Update: 3/25/2024                         #
#                                                 #
#  Description: Logger for the drone's flight     #
#               controller. Logs commands sent to #
#               the drone and responses received  #
#               from the drone, as well as the    #
#               latency between the two. Stores   #
#               commands in a python list that    #
#               can be accessed later.            # 
###################################################

# Required Imports
from datetime import datetime

class CommandResponseLogger:
    
    def __init__(self):
        self.log = []

    # Add a command to the event log
    def log_command(self, command: str):
        new_event = self._LogEvent(command, len(self.log))
        self.log.append(new_event)
    
    # Add a response to the most recent command event in the event log
    def log_reponse(self, response: str):
        self.log[-1].add_response(response)

    # Record a timeout for the most recent command event in the event log
    def log_time_out(self, time_out: bool):
        self.log[-1].update_time_out(time_out)
        
    # Save the log to a local file for analysis
    def save_log(self):
        with open('CommandResponseLog.txt', 'w') as file:
            for event in self.log:
                # Write each event to the log file
                file.write(str(event) + '\n')
    
    # Outline log event objects
    class _LogEvent:
        
        def __init__(self, command: str, id: int):
            self.command = command
            self.response = None
            self.id = id

            self.start_time = datetime.now()
            self.end_time = None
            self.latency = None

            self.time_out_occured = "No"
        
        def __str__(self):
            # Make list of return strings for this event
            ret_str_list = []
            
            # Copy Event ID and Command sent
            ret_str_list.append("Event ID: " + str(self.id) + "\n")
            ret_str_list.append("Command: " + self.command + "\n")
            
            # Copy Response
            if(self.response == None):
                ret_str_list.append("Response: None\n")
            else:
                ret_str_list.append("Response: " + str(self.response) + "\n")
            
            # Copy Command Sent Time
            if(self.start_time == None):
                ret_str_list.append("Command Sent Time: N/A\n")
            else:
                ret_str_list.append("Command Sent Time: " + str(self.start_time) + "\n")
            
            # Copy Response Received Time
            if(self.end_time == None):
                ret_str_list.append("Response Received Time: N/A\n")
            else:
                ret_str_list.append("Response Received Time: " + str(self.end_time) + "\n")

            # Copy Latency
            if(self.latency == None):
                ret_str_list.append("Latency: N/A\n")
            else:
                ret_str_list.append("Latency: " + str(self.latency) + "\n")

            # Copy (If) Time Out Occurred
            ret_str_list.append("Time Out Occurred: " + self.time_out_occured + "\n")

            # Join and return all items
            ret_str = "".join(ret_str_list) 
            return ret_str

        # Add a reponse to this event
        def add_response(self, response: str):
            self.response = str(response)
            # Calculating total time taken to execute command
            self.end_time = datetime.now()
            self.latency = (self.end_time-self.start_time).total_seconds()

        # Record whether or not a time out occurred for this event
        def update_time_out(self, time_out: bool):
            if(time_out):
                self.time_out_occured = "Yes"
            else:
                self.time_out_occured = "No"
        
        # Check if a response was received for the command sent
        def got_response(self):
            if self.response is None:
                return False
            else:
                return True

        # Get the raw response value
        def get_raw_response(self):
            return self.response
        
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
            raw_att = self.response.split(';')
            att_data = (self.int_response(raw_att[0]), self.int_response(raw_att[1]), self.int_response(raw_att[2]))
            return att_data
        
        # Process an acceleration response
        def acceleration_response(self):
            raw_acc = self.response.split(';')
            acc_data = (self.float_response(raw_acc[0]), self.float_response(raw_acc[1]), self.float_response(raw_acc[2]))
            return acc_data

        # Process a temperature response
        def temp_response(self):
            raw_temp = self.response.split('~')
            temp = (self.int_response(raw_temp[0]) + self.int_response(raw_temp[1]))/2
            return temp

        # Correctly process response
        def get_response(self):
            if 'attitude?' in self.command:
                return self.attitude_response()
            elif 'acceleration?' in self.command:
                return self.acceleration_response()
            elif 'temp?' in self.command:
                return self.temp_response()
            elif 'baro?' in self.command or 'speed?' in self.command:
                return self.float_response(self.response)
            elif '?' not in self.command:
                return self.get_raw_response()
            else:
                return self.int_response(self.response)


