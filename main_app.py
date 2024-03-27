###################################################
#        Autonomous Drone Main Control Hub        #
#                                                 #
#   Co-Authors: Jake Richardson, Alex Passin,     #
#               and Alex Longo.                   #
#                                                 #
#         Date: 3/6/2024                          #
#                                                 #
#  Description: TBD                               #
###################################################

# Imports:
#from djitellopy import tello
#from easytello import tello
import DroneFlightController

# Basic Test Code:
drone = DroneFlightController.DroneFlightController(True, True)
drone.takeoff()
drone.wait(2)


attitude = drone.get_attitude()
print(attitude)


drone.wait(2)
drone.land()
drone.save_log()