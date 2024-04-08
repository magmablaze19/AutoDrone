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

# Old Imports:
#from djitellopy import tello
#from easytello import tello
#import DroneFlightController

# New Imports:
import time
import cv2
import threading
from djitellopy import tello
from tkinter import *
from PIL import Image, ImageTk

class MainApp:
    def __init__(self):
        # Prepare our GUI window
        self.root = Tk()  # Initialize the Tkinter window
        self.root.title("Tello Drone Control GUI with Video Stream")  # Add a title to the window
        self.root.minsize(800, 600)  # Set the minimum gui size

        # Initialize the video stream capture label
        self.cap_lbl = Label(self.root)

        # Prepare our drone object
        self.drone = tello.Tello()  # Initialize the drone
        self.drone.connect()  # Connect to the drone
        self.drone.streamon()  # Turn on the drones video stream

        # Initialize variables involving drone functionalities
        self.frame = self.drone.get_frame_read()  # variable to get the video frames from the drone

        ### **** NEW **** ###
        # this is to store the joystick rc values as they are updated in realtime.
        self.rc_controls = [0, 0, 0, 0]  # the initial movement velocity values for lr, fb, ud, and yaw motions
        ### ************* ###

    def takeoff_land(self):
        """Set the command for the takeoff/land button depending on the drones flying state"""
        if self.drone.is_flying:
            threading.Thread(target=lambda: self.drone.land()).start()
        else:
            threading.Thread(target=lambda: self.drone.takeoff()).start()

    ### **** NEW METHOD **** ###
    def update_joystick(self):
        """Method to update joystick values."""
        try:
            
            # Map joystick values to specific RC control channels
            self.rc_controls[0] = right_joystick_x  # lr RC value
            self.rc_controls[1] = right_joystick_y  # fb RC value
            self.rc_controls[2] = left_joystick_y  # ud RC value
            self.rc_controls[3] = left_joystick_x  # yaw RC value

            # If rc control values aren't zero then send them to the drone using the send_rc_control(lr, fb, ud, yv) command.
            if self.rc_controls != [0, 0, 0, 0]:
                self.drone.send_rc_control(self.rc_controls[0], self.rc_controls[1], self.rc_controls[2], self.rc_controls[3])

            # and if not zero then send the equivalent command for the drone to hover in place
            else:
                self.drone.send_rc_control(0, 0, 0, 0)
            # Call the update_joystick method again after a delay (50 milliseconds)
            self.root.after(50, self.update_joystick)

        # Handle exceptions that may occur during joystick update
        except Exception as joystickUpdateException:
            print(f"Exception occurred when updating joystick values.\nJoystickUpdateException: {joystickUpdateException}")
    ### ************* ###

    def run_app(self):
        """Method to run the application."""
        try:
            # Pack the video stream label to the GUI window
            self.cap_lbl.pack(anchor="center")

            # Call the video_stream method to start displaying video
            self.video_stream()

            ### **** NEW **** ###
            # Call the update_joystick method to start the joystick control
            self.update_joystick()
            ### ************* ###

            # Start the tkinter main loop
            self.root.mainloop()
        except Exception as runAppException:
            print(f"Exception occurred when running the application.\nrunAppException: {runAppException}")
        finally:
            # When the root window is exited out of ensure to clean up any resources.
            self.cleanup()

    def video_stream(self):
        """Method to display video stream."""
        try:
            # Define the height and width to resize the current frame to
            h = 480
            w = 720

            # Read a frame from our drone
            frame = self.frame.frame

            frame = cv2.resize(frame, (w, h))

            # Convert the current frame to the rgb colorspace
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)

            # Convert this to a Pillow Image object
            img = Image.fromarray(cv2image)

            # Convert this then to a Tkinter compatible PhotoImage object
            imgtk = ImageTk.PhotoImage(image=img)

            # Place the image label at the center of the window
            self.cap_lbl.pack(anchor="center", pady=15)

            # Set it to the photo image
            self.cap_lbl.imgtk = imgtk

            # Configure the photo image as the displayed image
            self.cap_lbl.configure(image=imgtk)

            # Update the video stream label with the current frame
            # by recursively calling the method itself with a delay.
            self.cap_lbl.after(5, self.video_stream)
        except Exception as videoStreamException:
            print(f"Exception occurred when updating the video stream.\nvideoStreamException: {videoStreamException}")

    def cleanup(self) -> None:
        """Method for cleaning up resources."""
        try:
            # Release any resources
            print("Cleaning up resources...")
            self.drone.end()
            self.root.quit()  # Quit the Tkinter main loop
            exit()
        except Exception as e:
            print(f"Error performing cleanup: {e}")


if __name__ == "__main__":
    # Initialize the GUI
    gui = MainApp()

    # Call the run_app method to run tkinter mainloop
    gui.run_app()


