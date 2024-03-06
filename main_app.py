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
from djitellopy import tello


# Basic Test Code:
drone = tello.Tello()
drone.takeoff()
drone.land()