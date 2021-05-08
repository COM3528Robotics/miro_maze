import rospy

import time
import sys
import os

import cv2
from apriltag_perception import AprilTagPerception

try:  # For convenience, import this util separately
    from miro2.lib import wheel_speed2cmd_vel  # Python 3
except ImportError:
    from miro2.utils import wheel_speed2cmd_vel  # Python 2

from sensor_msgs.msg import JointState

# ROS cmd_vel (velocity control) message
from geometry_msgs.msg import TwistStamped
# MiRo-E interface
import miro_ros_interface as mri

# MiRo-E parameters
import miro_constants as con

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

    def getFocal(atp, image):
        tags = atp.detect_tags(image)
        if tags is None:
            print('No AprilTags in view!')
            return image, None, None
        else:
            focal_length, image = MiRoClient.getFocalLength(atp, tags, image)
            return image, tags, focal_length

    def getFocalLength(atp, tags, image):
        focal_length = None # ?
        tag_size = 1 # ?
        tag_distance = 2 # ?
        
        for t, _ in enumerate(tags):
            # Draw April Tag on screen
            atp.draw_box(image, tags[t], colour='green')
            atp.draw_center(image, tags[t], colour='red')

            # Output either focal length or estimated distance on the image
            if focal_length is not None:
                est_distance = (tag_size * focal_length) / \
                    tags[t].apparent_size
                cv2.putText(image, 'Distance: {0:.2f}cm'.format(est_distance), tuple(tags[t].corners[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                return est_distance, image
            else:
                est_focal_length = (
                    tags[t].apparent_size * tag_distance) / tag_size
                cv2.putText(image, 'Focal length: {0:.2f}'.format(est_focal_length), tuple(tags[t].corners[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                print('Estimated focal length: {}'.format(
                    est_focal_length))
                return est_focal_length, image



    def loop(self):

        miro_per = mri.MiRoPerception()

        # Set the actual size and distance of the AprilTag being used for calibration
        # (Units don't matter as long as you use the same for both)
        tag_size = 1
        tag_distance = 2

        # Enter a value here when you obtain a focal length to test your distance measurements are accurate
        focal_left = None
        focal_right = None

        atp = AprilTagPerception(size=tag_size, family='tag36h11')
        
        last_right_dist = None
        last_left_dist = None

        normal_speed = 1

        wheel_speed = [0,0]

        speed_left = normal_speed
        speed_right = normal_speed

        threshold_detection_failure = 10

        frames_failed_to_detect_tag = 0

        while True:
            # Not yet sure if undistorted images work better or worse for distance estimation
            image_left = miro_per.caml_undistorted
            image_right = miro_per.camr_undistorted

            # Try to read April Tag and calculate the focal length
            image_left, tags_left, focal_left = MiRoClient.getFocal(atp, image_left)
            image_right, tags_right, focal_right = MiRoClient.getFocal(atp, image_right)

            
            if focal_left is not None:
                last_left_dist = focal_left
                
            if focal_right is not None:
                last_right_dist = focal_right
            
            
            cv2.imshow('Left Camera: AprilTag calibration', image_left)
            cv2.imshow('Right Camera: AprilTag calibration2', image_right)
            cv2.waitKey(5)

            
            msg_cmd_vel = TwistStamped()

            if not tags_left and not tags_right:
                frames_failed_to_detect_tag += 1
            else:
                frames_failed_to_detect_tag = 0

            # Failed to find tags for a while
            if frames_failed_to_detect_tag >= threshold_detection_failure:
                # Shake? Rotate? to find tag
                speed_left = normal_speed
                speed_right = -normal_speed
            else:
                # Tags found
                # Adjust speed to follow the April Tag
                if last_left_dist is not None and last_right_dist is not None:

                    
                    delta_focal = last_left_dist - last_right_dist
                    
                    speed_modifier = 0
                    # we can use delta, ratio, etc...
                    if delta_focal > 0:
                        speed_modifier = 0.05
                    else:
                        speed_modifier = -0.05

                    # last_delta?

                    # last_left_dist / last_left_dist - last_right_dist

                    
                    speed_left = normal_speed + speed_modifier
                    speed_right = normal_speed - speed_modifier

                # Tags not found
                # just move forward if hasn't seen both distances at least once
                else:
                    speed_left = normal_speed
                    speed_right = normal_speed

            wheel_speed = [speed_left, speed_right]
        
            # Convert wheel speed to command velocity (m/sec, Rad/sec)
            (dr, dtheta) = wheel_speed2cmd_vel(wheel_speed)

            # Update the message with the desired speed
            msg_cmd_vel.twist.linear.x = dr
            msg_cmd_vel.twist.angular.z = dtheta

            # Publish message to control/cmd_vel topic
            self.vel_pub.publish(msg_cmd_vel)

if __name__ == "__main__":
    main = MiRoClient()  # Instantiate class
    main.loop()  # Run the main control loop
