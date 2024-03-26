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
drone.wait(5)
drone.streamon()
drone.wait(5)
drone.cw(90)
drone.wait(5)
drone.ccw(180)
drone.wait(5)
drone.cw(90)
drone.wait(5)
drone.up(30)
drone.wait(5)
drone.down(30)
drone.wait(5)
drone.land()
drone.save_log()