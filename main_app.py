###################################################
#        Autonomous Drone Main Control Hub        #
#                                                 #
#       Author: Alex Longo                        #
#                                                 #
#         Date: 9/4/2024                          #
#                                                 #
#  Description: Main script used for conducting   #
#               payload testing. Script uses my   #
#               DroneFlightController class to    #
#               establish a connection and        #
#               interface with the drone. Then it #
#               tells the drone to takeoff, fly   #
#               five feet forward, turn 90 deg.   #
#               to the right, fly three feet      #
#               forward, and land.                #
###################################################


# Imports:
import DroneFlightController
import threading
import keyboard

# Create a Key Listener for Emergency Drone Shutoff
def key_listener():
    while True:
        keyboard.wait("e")  # Wait for the "E" Key Press
        drone.emergency()  # Activate Emergency shutoff for Drone

# Main Script For Payload Transport Test Flight
if __name__ == "__main__": 
    
    # Setup a new drone object and establish a connection to the drone
    drone = DroneFlightController.DroneFlightController()

    # Create a thread to listen for keyboard input continuously
    key_thread = threading.Thread(target=key_listener, daemon=True)
    key_thread.start()

    # Send Takeoff Command
    drone.takeoff()

    # Send Command to Fly 5ft (152 cm) forward
    drone.forward(152)

    # Send Command to Turn 90 deg. to the right
    drone.cw(90)

    # Send Command to Fly 3ft (91 cm) forward
    drone.forward(91)

    # Send Land Command
    drone.land()

