from Follow import Follow
from Learning import Learning
from constants import Action, Maze
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

class MiRoClient:

    """
    Script settings below
    """
    TICK = 0.01  # This is the update interval for the main control loop in secs
    CAM_FREQ = 1  # Number of ticks before camera gets a new frame, increase in case of network lag
    NODE_EXISTS = False  # Disables (True) / Enables (False) rospy.init_node
    SLOW = 0.1  # Radial speed when turning on the spot (rad/s)
    FAST = 0.7  # Linear speed when kicking the ball (m/s)
    DEBUG = True  # Set to True to enable debug views of the cameras

    DEBUG_SPEED = False
    DEBUG_EST = False
    DEBUG_ACTION = True
    DEBUG_FOLLOW = False
    DEBUG_DECISION = True


    TAG_SIZE = 1

    SPEED = 0.33
    ROTATE_SPEED = 0.05

    DISTANCE_SAMPLE_SIZE = 5
    THRESHOLD_DISTANCE = 1.9
    
    def __init__(self):
        # robot name
        topic_base_name = "/" + os.getenv("MIRO_ROBOT_NAME")
        
        self.vel_pub = rospy.Publisher(topic_base_name + "/control/cmd_vel", TwistStamped, queue_size=0)
        self.pub_kin = rospy.Publisher(topic_base_name + "/control/kinematic_joints", JointState, queue_size=0)

        self.miro_per = mri.MiRoPerception()
        self.atp = AprilTagPerception(size=MiRoClient.TAG_SIZE, family='tag36h11')

        self.action = Action.FOLLOW
        self.target_tag = 0 # current target
        self.previous_decision_tag = None # the last tag it used to make a decision
        self.previous_action = None # the last action it made
        
        self.learning_model = Learning(read_predictions=True) # WIP but functional

        self.buffer_distance = [np.array([]), np.array([])]

    def set_wheel_speed(self, speed_left, speed_right):
        """Set Miro's wheel speed"""
        wheel_speed = [speed_left, speed_right]

        if MiRoClient.DEBUG_SPEED: print("Current Speed: %.2f, %.2f" % (speed_left, speed_right))

        # Convert wheel speed to command velocity (m/sec, Rad/sec)
        (dr, dtheta) = wheel_speed2cmd_vel(wheel_speed)

        # Update the message with the desired speed
        msg_cmd_vel = TwistStamped()
        msg_cmd_vel.twist.linear.x = dr
        msg_cmd_vel.twist.angular.z = dtheta

        # Publish message to control/cmd_vel topic
        self.vel_pub.publish(msg_cmd_vel)

    def detect_new_tag(self):
        for index, image in enumerate(self.images):
            detected_tags = self.atp.detect_tags(image)

            if detected_tags:
                for tag in detected_tags:
                    if tag.id is not self.target_tag:
                        return tag.id

    def estimate_distance(self, target_tag):
        """Return a list of estimated distances to a specific tag for each given image"""
        tags_centre_x = []
        distances = []
        for index, image in enumerate(self.images):
            detected_tags = self.atp.detect_tags(image)
            
            tag_distance = None
            tag_centre_x = None
            

            if detected_tags:
                for tag in detected_tags:

                    if tag.id == target_tag:
                        tag_distance = tag.distance
                        tag_centre_x = tag.centre[0]

                        # Print distance on screen
                        if MiRoClient.DEBUG:
                            self.atp.draw_center(image, tag, colour='red')
                            cv2.putText(image, "Distance: %s" % (str(tag_distance)), tuple(tag.corners[1]),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                        break

            distances.append(tag_distance)
            tags_centre_x.append(tag_centre_x)

        if MiRoClient.DEBUG_EST: print("Estimated distance to tag %d are: %s" % (self.target_tag, str(distances)))
        return distances, tags_centre_x

    # TODO: Fix following
    def follow(self):
        """Follow a april tag and return True if MiRo reaches the tag, else False"""

        distances, dist_to_centre = self.estimate_distance(self.target_tag)
        
        for index in [0, 1]:
            self.buffer_distance[index] = np.append(self.buffer_distance[index], dist_to_centre[index])
            self.buffer_distance[index] = self.buffer_distance[index][-MiRoClient.DISTANCE_SAMPLE_SIZE:]

            try:
                if dist_to_centre[index] is None:
                    dist_to_centre[index] = stat.mean([d for d in self.buffer_distance[index] if d is not None])
            except:
                # If eye cannot see tag, assume its too far away
                dist_to_centre[index] = 640 if index == 0 else 0
        
        d_left = 640 - dist_to_centre[0]
        d_right = dist_to_centre[1]
        
        if MiRoClient.DEBUG_FOLLOW: print("Average distance: %s, %s" % (str(distances[0]), str(distances[1])))
        if MiRoClient.DEBUG_FOLLOW: print("Average distance: %s px, %s px" % (str(d_left), str(d_right)))

        # Tag is seen by both camera
        if d_left or d_right:
            # Calculate steering
            speed_left, speed_right = Follow.rule_delta_linear(d_left, d_right, scale=1/800, cap=100)

            base_speed = MiRoClient.SPEED - min(speed_left + speed_right, MiRoClient.SPEED)

            self.set_wheel_speed(base_speed - speed_left, base_speed - speed_right)
        # Cannot detect tag
        else:
            speed = MiRoClient.ROTATE_SPEED
            self.set_wheel_speed(0.01, -0.01)

        if self.target_tag in Maze.JUNCTIONS:
            threshold = MiRoClient.THRESHOLD_DISTANCE
        else:
            threshold = MiRoClient.THRESHOLD_DISTANCE

        # Return true if distance from either camera is within threshold
        return distances[0] and distances[0] < threshold or \
            distances[1] and distances[1] < threshold

    # needs to have the current state as a param
        # and the previous seen descision tag
    def make_decision(self):
        """ Make decision """
        # TODO: Reached ending tag 
        print("Current tag: %s, Last tag is: %s, Last Action is: %s" %\
            (self.target_tag, self.previous_decision_tag, self.previous_action)) 
        
        if self.target_tag in Maze.END_TAGS:
            if self.target_tag in Maze.REWARDS:
                self.learning_model.learn(self.previous_decision_tag, self.previous_action, 1)
            else:
                self.learning_model.learn(self.previous_decision_tag, self.previous_action, -1)

            print("final learned predictions")
            print(self.learning_model.predicted_reward)
            self.learning_model.export()
            self.action = Action.STOP

        # reinforcment learning descision
        elif self.target_tag in Maze.JUNCTIONS:
            if MiRoClient.DEBUG_ACTION: print("Making Decision")

            self.learning_model.learn(
                self.previous_decision_tag, 
                self.previous_action, 
                self.learning_model.predict_next_reward(self.target_tag)
            )
            # self.action = random.choice([Action.TURN_LEFT, Action.TURN_RIGHT])
            self.action = self.learning_model.decide(self.target_tag)
            self.previous_action = self.action
            self.previous_decision_tag = self.target_tag
        
        # corners to the left
        elif self.target_tag in Maze.CORNERS_LEFT:
            self.action = Action.TURN_LEFT

        # corners to the right
        else:
            self.action = Action.TURN_RIGHT

        if MiRoClient.DEBUG_DECISION: 
            if self.action is Action.TURN_LEFT:
                print("Deciding to turn left")
            else:
                print("Deciding to turn right")

    def loop(self):
        
        continue_condition = True

        while(self.action is not Action.STOP):
            # Update robot vision
            self.images = [self.miro_per.caml_undistorted, self.miro_per.camr_undistorted]

            # Follow the current tag
            if self.action is Action.FOLLOW:

                has_reach_end = self.follow()

                # Make decision when it reaches the tag
                if has_reach_end:
                    self.action = Action.MAKE_DECISION
        
            # Decide the next action
            elif self.action is Action.MAKE_DECISION:
                self.make_decision()

            # Rotate until a new tag is found, then change action to FOLLOW
            else: 
                # Rotate LEFT
                if self.action is Action.TURN_LEFT:
                    self.set_wheel_speed(-MiRoClient.ROTATE_SPEED, MiRoClient.ROTATE_SPEED)

                # Rotate RIGHT
                else:
                    self.set_wheel_speed(MiRoClient.ROTATE_SPEED, -MiRoClient.ROTATE_SPEED)

                new_tag = self.detect_new_tag()
                
                if new_tag is not None:
                    self.target_tag = new_tag
                    self.action = Action.FOLLOW

                    if MiRoClient.DEBUG_ACTION: print("Following tag %d" % self.target_tag)

            # Show Camera feeds
            cv2.imshow('Camera: AprilTag calibration', np.hstack(self.images))
            cv2.waitKey(50)
        
if __name__ == "__main__":
    main = MiRoClient()  # Instantiate class
    main.loop()  # Run the main control loop
