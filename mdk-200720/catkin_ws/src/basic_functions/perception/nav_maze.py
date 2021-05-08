import cv2
from apriltag_perception import AprilTagPerception

try:  # For convenience, import this util separately
    from miro2.lib import wheel_speed2cmd_vel  # Python 3
except ImportError:
    from miro2.utils import wheel_speed2cmd_vel  # Python 2

# ROS cmd_vel (velocity control) message
from geometry_msgs.msg import TwistStamped
import rospy
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
        self.vel_pub = rospy.Publisher(
            topic_base_name + "/control/cmd_vel", TwistStamped, queue_size=0
        )
    # Create a new publisher to move the robot head
    self.pub_kin = rospy.Publisher(
        topic_base_name + "/control/kinematic_joints", JointState, queue_size=0
    )

    def loop(self):

        miro_per = mri.MiRoPerception()

        # Set the actual size and distance of the AprilTag being used for calibration
        # (Units don't matter as long as you use the same for both)
        tag_size = 1
        tag_distance = 2

        # Enter a value here when you obtain a focal length to test your distance measurements are accurate
        focal_length = None

        atp = AprilTagPerception(size=tag_size, family='tag36h11')

        while True:
            # Not yet sure if undistorted images work better or worse for distance estimation
            image = miro_per.caml_undistorted
            tags = atp.detect_tags(image)

            if tags is not None:

                for t, _ in enumerate(tags):
                    atp.draw_box(image, tags[t], colour='green')
                    atp.draw_center(image, tags[t], colour='red')

                    # Output either focal length or estimated distance on the image
                    if focal_length is not None:
                        est_distance = (tag_size * focal_length) / \
                            tags[t].apparent_size
                        cv2.putText(image, 'Distance: {0:.2f}cm'.format(est_distance), tuple(tags[t].corners[1]),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
                    else:
                        est_focal_length = (
                            tags[t].apparent_size * tag_distance) / tag_size
                        cv2.putText(image, 'Focal length: {0:.2f}'.format(est_focal_length), tuple(tags[t].corners[1]),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                        print('Estimated focal length: {}'.format(
                            est_focal_length))

                        msg_cmd_vel = TwistStamped()

                        # Desired wheel speed (m/sec)
                        wheel_speed = [0.1, 0.1]

                        # Convert wheel speed to command velocity (m/sec, Rad/sec)
                        (dr, dtheta) = wheel_speed2cmd_vel(wheel_speed)

                        # Update the message with the desired speed
                        msg_cmd_vel.twist.linear.x = dr
                        msg_cmd_vel.twist.angular.z = dtheta

                        # Publish message to control/cmd_vel topic
                        self.vel_pub.publish(msg_cmd_vel)

            else:
                print('No AprilTags in view!')

            cv2.imshow('AprilTag calibration', image)
            cv2.waitKey(5)


if __name__ == "__main__":
    main = MiRoClient()  # Instantiate class
    main.loop()  # Run the main control loop
