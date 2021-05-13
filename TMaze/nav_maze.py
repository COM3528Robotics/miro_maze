from utils import Utils

# MiRo-E interface
import basic_functions.miro_ros_interface as mri
# MiRo-E parameters
import basic_functions.miro_constants as con
from basic_functions.perception.apriltag_perception import AprilTagPerception

import rospy

import random
import statistics as stat

import time
import sys
import os

import numpy as np

import cv2

try:  # For convenience, import this util separately
    from miro2.lib import wheel_speed2cmd_vel  # Python 3
except ImportError:
    from miro2.utils import wheel_speed2cmd_vel  # Python 2

from sensor_msgs.msg import JointState
from geometry_msgs.msg import TwistStamped



# USAGE: Set MiRo in front of an example AprilTag
# (See here: https://april.eecs.umich.edu/software/apriltag)
# Enter the actual size of the tag and the distance from the camera, and ensure focal_length == None
# Run the script and note down the focal length given
# Enter the focal length and re-run the script; adjust MiRo's distance from the tag and check for accuracy


class MiRoClient:

    """
    Script settings below
    """
    TICK = 0.01  # This is the update interval for the main control loop in secs
    CAM_FREQ = 1  # Number of ticks before camera gets a new frame, increase in case of network lag
    NODE_EXISTS = False  # Disables (True) / Enables (False) rospy.init_node
    SLOW = 0.1  # Radial speed when turning on the spot (rad/s)
    FAST = 0.7  # Linear speed when kicking the ball (m/s)
    DEBUG = False  # Set to True to enable debug views of the cameras

    TAG_SIZE = 1

    SPEED = 1

    BUFFER_SIZE_DISTANCE = 10
    THRESHOLD_DISTANCE = 2
        

    def __init__(self):
        # robot name
        topic_base_name = "/" + os.getenv("MIRO_ROBOT_NAME")
        
        self.vel_pub = rospy.Publisher(
            topic_base_name + "/control/cmd_vel", TwistStamped, queue_size=0
        )

        # Create a new publisher to move the robot head
        self.pub_kin = rospy.Publisher(
            topic_base_name + "/control/kinematic_joints", JointState, queue_size=0
        )

        self.miro_per = mri.MiRoPerception()
        self.atp = AprilTagPerception(size=MiRoClient.TAG_SIZE, family='tag36h11')

        self.buffer_distance = [np.array([]), np.array([])]

    def decide(self, tag_id):
        decision = ""

        # reinforcment learning descision
        # hidden left
        if tag_id == 0:
            decision = random.choice(["left", "right"])
        # hidden right
        elif tag_id == 3:
            decision = random.choice(["left", "right"])

        # fixed
        elif tag_id == 1:
            decision = 'left'
        elif tag_id == 2:
            decision = 'right'
            
        return decision

    def set_wheel_speed(self, speed_left, speed_right):
        """Set Miro's wheel speed"""
        wheel_speed = [speed_left, speed_right]
        if MiRoClient.DEBUG: print("Current Speed: %.2f, %.2f" % (speed_left, speed_right))

        # Convert wheel speed to command velocity (m/sec, Rad/sec)
        (dr, dtheta) = wheel_speed2cmd_vel(wheel_speed)

        # Update the message with the desired speed
        msg_cmd_vel = TwistStamped()
        msg_cmd_vel.twist.linear.x = dr
        msg_cmd_vel.twist.angular.z = dtheta

        # Publish message to control/cmd_vel topic
        self.vel_pub.publish(msg_cmd_vel)

    def estimate_distance(self, tag_id):
        """Return a list of estimated distances to a specific tag for each given image"""
        estimated_distances = []
        for index, image in enumerate(self.images):
            detected_tags = self.atp.detect_tags(image)
            
            tag_distance = None

            if detected_tags:
                for tag in detected_tags:
                    if tag.id == tag_id:
                        tag_distance = tag.distance

                        # Print distance on screen
                        if MiRoClient.DEBUG:
                            self.atp.draw_box(image, tag, colour='green')
                            self.atp.draw_center(image, tag, colour='red')
                            cv2.putText(image, "Distance: %s" % (str(tag_distance)), tuple(tag.corners[1]),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                        break

            estimated_distances.append(tag_distance)

        if MiRoClient.DEBUG: print("Estimated distance to tag %d are: %s" % (tag_id, str(estimated_distances)))
        return estimated_distances

    def follow(self, tag_id):
        """Follow a april tag and return True if MiRo reaches the tag, else False"""

        distances = self.estimate_distance(tag_id)
        d = [0, 0]
        for index in [0, 1]:
            self.buffer_distance[index] = np.append(self.buffer_distance[index], distances[index])
            self.buffer_distance[index] = self.buffer_distance[index][-MiRoClient.BUFFER_SIZE_DISTANCE:]

            try:
                d[index] = stat.mean([d for d in self.buffer_distance[index] if d is not None])
            except:
                d[index] = None
        
        d_left = d[0]
        d_right = d[1]
        
        print("Average distance %s %s" % (str(d_left), str(d_right)))
        
        speed_left_mod = 0
        speed_right_mod = 0

        # Tag is seen by both camera
        if d_left and d_right:
            d_delta = d_left - d_right

            """ Method 1: linear
            speed_mod = d_delta
            """

            # Method 2: Bounding 
            speed_mod = Utils.bound(d_delta, 0.05)

            # Method 3: Sigmoid

            # if d_delta is positive, left camera is further away,
            # so left wheel need to slow down,
            # and vice versa
            speed_left_mod = -speed_mod
            speed_right_mod = speed_mod

        # Tag is only seen by one camera
        elif d_left or d_right:
            speed = 0.5
            speed_left_mod = -speed if d_left else speed
            speed_right_mod = -speed if d_right else speed

            speed_left_mod -= MiRoClient.SPEED
            speed_right_mod -= MiRoClient.SPEED 

        # Cannot detect tag
        else:
            speed_left_mod = 0
            speed_right_mod = 0

        speed_left = MiRoClient.SPEED + speed_left_mod
        speed_right = MiRoClient.SPEED + speed_right_mod

        self.set_wheel_speed(speed_left, speed_right)

        # Return true if distance from either camera is within threshold
        return d_left and d_left < MiRoClient.THRESHOLD_DISTANCE or \
            d_right and d_right < MiRoClient.THRESHOLD_DISTANCE

    def detect_new_tag(self, current_tag_id):
        new_tag_id = None

        for index, image in enumerate(self.images):
            if new_tag_id is not None:
                detected_tags = self.atp.detect_tags(image)

                if detected_tags:
                    for tag in detected_tags:
                        if tag.id is not current_tag_id:
                            new_tag = tag.id
                            break

        return new_tag_id

    def loop(self):
        ACTION_FOLLOW = 1
        ACTION_TURN_LEFT = 2
        ACTION_TURN_RIGHT = 3
        ACTION_NEXT_DIRECTION = 4

        MiRoClient.SPEED = 0.5

        MiRoClient.DEBUG = True

        current_tag = 0
        action_flag = ACTION_FOLLOW
        continue_condition = True

        while(continue_condition):
            # Update robot vision
            self.images = [self.miro_per.caml_undistorted, self.miro_per.camr_undistorted]

            # Follow the current tag
            if action_flag is ACTION_FOLLOW:
                has_reach_end = self.follow(current_tag)

                if has_reach_end:
                    action_flag = ACTION_NEXT_DIRECTION
        
            # Decide the next action
            elif action_flag is ACTION_NEXT_DIRECTION:
                result = self.decide(current_tag)

                # TODO
                if result == 'left':
                    action_flag = ACTION_TURN_LEFT
                elif result == "right":
                    action_flag = ACTION_TURN_RIGHT

            # Rotate until a new tag is found, then change action to FOLLOW
            else: 
                # Rotate LEFT
                if action_flag is ACTION_TURN_LEFT:
                    self.set_wheel_speed(-MiRoClient.SPEED, MiRoClient.SPEED)

                # Rotate RIGHT
                else:
                    self.set_wheel_speed(MiRoClient.SPEED, +MiRoClient.SPEED)

                new_tag = self.detect_new_tag(current_tag)

                if new_tag is not None:
                    current_tag = new_tag
                    action_flag = ACTION_FOLLOW


            numpy_horizontal = np.vstack(self.images)
            cv2.imshow('Camera: AprilTag calibration', numpy_horizontal)
            cv2.waitKey(5)
        
if __name__ == "__main__":
    main = MiRoClient()  # Instantiate class
    main.loop()  # Run the main control loop
