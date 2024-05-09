# Autonmous Quadcopter
A small-scale autonomous drone that uses camera data and visual odometry algorithms for indoor navigation. Our goal is to develop a computationally-lightweight system that will allow the drone to operate autonomously using solely its on-board computing resources.  
  
**Please Note: This is still under active development**  
  
### Hardware
Ryze Tello Drone (https://www.ryzerobotics.com/tello)  

### Authors
Alex Longo (https://github.com/BlockadeRunner)  
Alex Passin (https://github.com/magmablaze19)  
Jake Richardson (https://github.com/jtrichWM)  

### File Descriptions:
**main_app.py** ~ Main script used for conducting payload testing. Script uses the DroneFlightController class to establish a connection and interface with the drone. Then it tells the drone to takeoff, fly five feet forward, turn 90 deg to the right, fly three feet forward, and land.

**DroneFlightController.py** ~ Main flight controller for sending commands to the drone and receiving responses from the drone. Serves as an interface for the drone and provides methods for interacting with it. Also logs flight events using CommandResponseLogger.py

**CommandResponseLogger.py** ~ Logger for the drone's flight controller. Logs commands sent to the drone and responses received from the drone, as well as the latency between the two. Stores commands in a python list that can be accessed later.

