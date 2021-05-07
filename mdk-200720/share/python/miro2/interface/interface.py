#	@section COPYRIGHT
#	Copyright (C) 2020 Consequential Robotics Ltd
#	
#	@section AUTHOR
#	Consequential Robotics http://consequentialrobotics.com
#	
#	@section LICENSE
#	For a full copy of the license agreement, and a complete
#	definition of "The Software", see LICENSE in the MDK root
#	directory.
#	
#	Subject to the terms of this Agreement, Consequential
#	Robotics grants to you a limited, non-exclusive, non-
#	transferable license, without right to sub-license, to use
#	"The Software" in accordance with this Agreement and any
#	other written agreement with Consequential Robotics.
#	Consequential Robotics does not transfer the title of "The
#	Software" to you; the license granted to you is not a sale.
#	This agreement is a binding legal agreement between
#	Consequential Robotics and the purchasers or users of "The
#	Software".
#	
#	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
#	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
#	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
#	PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
#	OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
#	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
#	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#	

################################################################

# python
import os
import math
import numpy as np
import time
import miro2 as miro
from threading import Thread

# ROS
import rospy
from std_msgs.msg import Float32MultiArray, UInt32MultiArray, UInt16MultiArray, UInt8MultiArray, UInt16, Int16MultiArray, UInt32
from geometry_msgs.msg import TwistStamped, Vector3
from sensor_msgs.msg import JointState, BatteryState, Imu, Range, CompressedImage, Image

#Open CV
import cv2
from cv_bridge import CvBridge, CvBridgeError

#interface
from audio import *
from vision import *

################################################################

#Should import common.py from share/web?
DIR_STATE=os.getenv('MIRO_DIR_STATE')
FILE_WEB_CMD=DIR_STATE + "/client_web.cmd"

class PlatformInterface:

	def __init__(self, mode=None, enable_pose_ctrl=True, enable_cliff_reflex=True):

		# mode
		if mode is None:
			mode = ''

		# report
		if not 'silent' in mode:
			print '[interface] connecting to robot...',

		#Initialise
		self.clap_detector = ClapDetector()
		self.vision = Vision()

		# state
		self.m_ready = True
		self.web_cmd = ""

		# topic root
		self.topic_root = '/' + os.getenv("MIRO_ROBOT_NAME") + '/'

		#Configure ROS interface
		#Publishers
		self.velocity_pub = rospy.Publisher(self.topic_root + "control/cmd_vel", TwistStamped, queue_size=0)
		self.cosmetic_joints_pub = rospy.Publisher(self.topic_root + "control/cosmetic_joints", Float32MultiArray, queue_size=0)
		self.illum_pub = rospy.Publisher(self.topic_root + "control/illum", UInt32MultiArray, queue_size=0)
		self.kinematic_joints_pub = rospy.Publisher(self.topic_root + "control/kinematic_joints", JointState, queue_size=0)
		self.audio_tone_pub = rospy.Publisher(self.topic_root + "control/tone", UInt16MultiArray, queue_size=0)
		# self.param_pub = rospy.Publisher(self.topic_root + "control/params", Float32MultiArray, queue_size=0)
		self.push_pub = rospy.Publisher(self.topic_root + "core/mpg/push", miro.msg.push, queue_size=0)
		self.pub_flags = rospy.Publisher(self.topic_root + "control/flags", UInt32, queue_size=0)

		#Create objects to hold published data
		self.velocity = TwistStamped()

		self.kin_joints = JointState()
		self.kin_joints.name = ["tilt", "lift", "yaw", "pitch"]
		self.kin_joints.position = [0.0, miro.constants.LIFT_RAD_CALIB, 0.0, 0.0]

		self.cos_joints = Float32MultiArray()
		self.cos_joints.data = [0.0, 0.5, 0.0, 0.0, 0.0, 0.0]
		self.wag = False
		self.wag_phase = 0.0
		self.wag_rate = 0

		self.tone = UInt16MultiArray()
		self.tone.data = [0, 0, 0]

		# LEDs off, unless user requests otherwise
		self.illum = UInt32MultiArray()
		self.illum.data = [0x00FFFFFF, 0x00FFFFFF, 0x00FFFFFF, 0x00FFFFFF, 0x00FFFFFF, 0x00FFFFFF]

		# Create push object
		self.msg_push = miro.msg.push()

		# self.params = Float32MultiArray()
		# self.params.data = [721.0, 15.0]

		#Create Variables to store recieved data
		self.sonar_range = None
		self.light_array = [None, None, None, None]
		self.cliff_array = None
		self.head_touch = None
		self.body_touch = None
		self.imu_head = None
		self.imu_body = None

		#Variables for IMU calculations
		self.imu_head_prev = None
		self.imu_body_prev = None
		self.shake_head = 0.0
		self.shake_body = 0.0
		self.shake_head_smooth = np.array([0.0, 0.0, 0.0])
		self.shake_body_smooth = np.array([0.0, 0.0, 0.0])
		self.shake_smooth_i = 0
		self.shake_thresh = 2.0
		self.time_at_head_shake = -60.0
		self.time_at_body_shake = -60.0
		self.time_at_any_shake = -60.0


		#Construct kinematic Chain to model miro motion
		self.kc = miro.utils.kc_interf.kc_miro()

		#Arrays to hold image topics
		self.cam_left_image = None
		self.cam_right_image = None

		#Create object to convert ROS images to OpenCV format
		self.image_converter = CvBridge()

		#Create resource for controlling body_node
		self.pars = miro.utils.PlatformPars()
		self.cam_model = miro.utils.CameraModel()
		self.frame_w = 0
		self.frame_h = 0

		#Create resource for using Pose Control Module if enabled
		self.pose_ctrl = False
		if enable_pose_ctrl:
			self.pose_ctrl = True

		self.pose_controller = miro.lib.PoseController()
		self.cmd_vel = miro.lib.DeltaPose()
		self.adjusted_velocity = TwistStamped()

		#Disable Cliff Reflex using control flags if requested
		default_flags = miro.constants.PLATFORM_D_FLAG_DISABLE_STATUS_LEDS
		msg = UInt32()
		msg.data = default_flags
		if not enable_cliff_reflex:
			msg.data |= miro.constants.PLATFORM_D_FLAG_DISABLE_CLIFF_REFLEX
		self.pub_flags.publish(msg)


		#Timer variables
		self.pause_flag = False
		self.timer_end_time = 0.0
		self.time_now = 0.0
		self.time_limit = 0

		#Touch Time
		self.time_at_body_touch = -60.0
		self.time_at_head_touch = -60.0
		self.time_at_any_touch = -60.0

		# timer watchdog
		self.timer_watchdog_t = 0
		self.timer_watchdog_n = 0

		#Start thread
		self.updated = False
 		self.update_thread = Thread(target=self.update)
 		self.update_thread.start()
		self.thread_running = True

		#Subscribe to sensors
		self.touch_body_sub = rospy.Subscriber(self.topic_root + "sensors/touch_body", UInt16, self.touch_body_callback, tcp_nodelay=True)
		self.touch_head_sub = rospy.Subscriber(self.topic_root + "sensors/touch_head", UInt16, self.touch_head_callback, tcp_nodelay=True)
		self.mics_sub = rospy.Subscriber(self.topic_root + "sensors/mics", Int16MultiArray, self.mics_callback, tcp_nodelay=True)

		#Subscribe to Camera topics
		self.cam_left_sub = rospy.Subscriber(self.topic_root + "sensors/caml/compressed", CompressedImage, self.cam_left_callback, tcp_nodelay=True)
		self.cam_right_sub = rospy.Subscriber(self.topic_root + "sensors/camr/compressed", CompressedImage, self.cam_right_callback, tcp_nodelay=True)

		# last subscription is to sensors_package because that drives the clock
		self.sensors_sub = rospy.Subscriber(self.topic_root + "sensors/package", miro.msg.sensors_package, self.sensors_callback, tcp_nodelay=True)

		# Subscribe to kinematic_joints
		self.kinematic_joints_sub = rospy.Subscriber("/miro/sensors/kinematic_joints", JointState, self.kin_callback, tcp_nodelay=True)

		# handle wait
		if not 'nowait' in mode:
			time.sleep(1.0)

		# report
		if not 'silent' in mode:
			print 'OK'

	def yield_cpu(self):

		# just yield the CPU briefly
		time.sleep(0.01)

	def get_time(self):

		# typically, we want to use the physical clock
		return self.time_now

		# we can use the wallclock, as an alternative, but it's not right
		#return time.time()

	def set_time_limit(self, t):

		self.time_limit = t

	def wait_for_time_limit(self):

		# get time
		t = self.get_time()

		# watchdog
		if t == self.timer_watchdog_t:
			self.timer_watchdog_n += 1
			if self.timer_watchdog_n == 100:
				print "timer watchdog fired"
				return False
		self.timer_watchdog_n = 0
		self.timer_watchdog_t = t

		# if not yet reached time limit
		if t < self.time_limit:
			return True

		# otherwise, passed time limit
		self.time_limit = 0
		return False

	def compute_shake(self, imu_curr, imu_prev):

		#Calculate difference to previous value
		x = imu_curr.x - imu_prev.x
		y = imu_curr.y - imu_prev.y
		z = imu_curr.z - imu_prev.z

		#compute magnitude
		mag = np.sqrt(np.square(x) + np.square(y) + np.square(z))
		return mag

	def compute_shakes(self):

		# If stored value exists, compute shake
		if self.imu_head_prev is not None:
			shake_head_inst = self.compute_shake(self.imu_head, self.imu_head_prev)
			shake_body_inst = self.compute_shake(self.imu_body, self.imu_body_prev)

			#Smooth magnitudes using 2 previous values
			if self.shake_smooth_i == len(self.shake_head_smooth):
				self.shake_smooth_i = 0
			self.shake_head_smooth[self.shake_smooth_i] = shake_head_inst
			self.shake_body_smooth[self.shake_smooth_i] = shake_body_inst
			self.shake_head = np.mean(self.shake_head_smooth)
			self.shake_body = np.mean(self.shake_body_smooth)
			self.shake_smooth_i += 1

			if self.shake_head > self.shake_thresh:
				self.time_at_head_shake = self.time_now
				self.time_at_any_shake = self.time_now
			if self.shake_body > self.shake_thresh:
				self.time_at_body_shake = self.time_now
				self.time_at_any_shake = self.time_now

			# print "inst: ", shake_head_inst, ", mean: ", self.shake_head, " thresh: ", self.shake_thresh

		#Store new values as previous values
		self.imu_head_prev = self.imu_head
		self.imu_body_prev = self.imu_body

	def sensors_callback(self, message):

		# we use this call to advance the clock
		self.time_now += 0.02

		self.sonar_range = message.sonar.range
		self.light_array = message.light.data
		self.cliff_array = message.cliff.data
		self.imu_body = message.imu_body.linear_acceleration
		self.imu_head = message.imu_head.linear_acceleration

		#Send wheel speed data to Pose Controller
		self.pose_controller.update_sensors(np.array(message.wheel_speed_opto.data))

		#Send IMU values to shake Detector
		self.compute_shakes()

		#These sensors need their own streams so they can be spoofed
		#self.head_touch =  message.touch_head.data
		#self.body_touch =  message.touch_body.data

	def touch_body_callback(self, message):
		self.body_touch = message.data
		if self.body_touch != 0:
			self.time_at_body_touch = self.time_now
			self.time_at_any_touch = self.time_now

	def touch_head_callback(self, message):
		self.head_touch = message.data
		if self.head_touch != 0:
			self.time_at_head_touch = self.time_now
			self.time_at_any_touch = self.time_now

	def mics_callback(self, message):
		self.clap_detector.detect_clap(message.data, self.time_now)

	def kin_callback(self, msg):
	    self.kc.setConfig(msg.position)

	def read_sonar_range(self):
		return self.sonar_range

	def read_light_level_list(self):
		return self.light_array

	def read_light_level(self, pos):
		if pos >= 0 and pos <4:
			return self.light_array[pos]

	def read_cliff_sensor(self, pos):
		if pos >= 0 and pos < 2:
			if self.cliff_array[pos] < 0.7:
				return True
			else:
				return False

	def read_cliff_sensor_list(self):
		return self.cliff_array

	def read_head_touch_sensors(self):
		#return self.head_touch

		# new list format
		return [bool(int(x)) for x in '{:014b}'.format(self.head_touch)]

	def read_body_touch_sensors(self):
		#return self.body_touch

		# new list format
		return [bool(int(x)) for x in '{:014b}'.format(self.body_touch)]

	def time_since_touch(self, body_pos):
		if body_pos not in ["head", "body", "all"]:
			print body_pos, "is not a a valid argument, enter \"head\", \"body\" or \"any\""
			return
		if body_pos == "head":
			return self.time_now - self.time_at_head_touch
		elif body_pos == "body":
			return self.time_now - self.time_at_body_touch
		elif body_pos == "any":
			return self.time_now - self.time_at_any_touch

	def read_imu(self, index):
		pass

	def shake(self, index, custom_thresh=None):
		if index not in ["head", "body", "all"]:
			print index, "is not a a valid argument, enter \"head\", \"body\" or \"any\""
			return
		if index == "head":
			shake_mag = self.shake_head
		elif index == "body":
			shake_mag = self.shake_body
		else:
			shake_mag = max(self.shake_head, self.shake_body)

		if custom_thresh is not None:
			thresh = custom_thresh
		else:
			thresh = self.shake_thresh

		if shake_mag > thresh:
		 	return True
		else:
			return False

	def time_since_shake(self, index):
		if index not in ["head", "body", "all"]:
			print index, "is not a a valid argument, enter \"head\", \"body\" or \"any\""
			return
		if index == "head":
			shake_time = self.time_at_head_shake
		elif index == "body":
			shake_time = self.time_at_body_shake
		else:
			shake_time = self.time_at_any_touch

		return self.time_now - shake_time

	def find_mirocube(self, cam_id=None):
		self.pause()
		if cam_id is not None:
			mirocube, dist = self.vision.detect_april(cam_id)
			index = cam_id
		else:
			mirocube, dist, index = self.vision.detect_april_both()

		if mirocube is None:
			return None

		return [mirocube.centre, dist, index]

	def find_mirocube_prop(self, cam_id=None, prop=None):
		self.pause()
		if cam_id is not None:
			mirocube, dist = self.vision.detect_april(cam_id)
			index = cam_id
		else:
			mirocube, dist, index = self.vision.detect_april_both()

		if mirocube is None:
			return None

		if prop is not None:
			if prop == "id":
				return mirocube.id
			elif prop == "loc":
				return mirocube.centre
			elif prop == "loc_x":
				return mirocube.centre[0]
			elif prop == "loc_y":
				return mirocube.centre[1]
			elif prop == "dist":
				return dist
			elif prop == "cam":
				return index
			else:
				print prop, "is not a a valid argument, enter \"id\", \"loc_x\", \"loc_y\", \"loc\", \"dist\" or \"cam\""
				return

		else:
			return mirocube


	def find_com(self, colour, cam_id, prop=None):

		com = self.vision.calc_com(colour, cam_id)

		if com == None:
			return None
		if prop == "loc":
			return com[0]
		elif prop == "loc_x":
			return com[0][0]
		elif prop == "loc_y":
			return com[0][1]
		elif prop == "area":
			return com[1]
		else:
			return com

	def find_shape(self, colour, vert, cam_id, prop=None):

		shape = self.vision.detect_shapes(colour, vert, cam_id)

		if shape == None:
			return None
		if prop == "loc":
			return shape[0]
		elif prop == "loc_x":
			return shape[0][0]
		elif prop == "loc_y":
			return shape[0][1]
		elif prop == "area":
			return shape[1]
		else:
			return shape

	def find_centre_colour(self, size, cam_id):
		colour = self.vision.calc_centre_colour(size, cam_id)
		return colour

	def find_ball(self, colour, cam_id, prop=None):
		self.pause()
		if cam_id < 0 or cam_id > 1:
			print("camera index should be 0 or 1")
			return None

		ball = self.vision.detect_ball(colour, cam_id)
		if ball is None:
			return None

		if prop == "loc":
			return ball[0]
		elif prop == "loc_x":
			return ball[0][0]
		elif prop == "loc_y":
			return ball[0][1]
		elif prop == "rad":
			return ball[1]
		else:
			return ball


	def clear_ball(self, cam_id):
		if cam_id < 0 or cam_id > 1:
			return
		self.vision.clear(cam_id)

	def clap(self):
		if self.clap_detector.have_seen_clap():
			return True
		else:
			return False

	def time_since_clap(self):
		if self.clap_detector.time_at_clap != None:
			return self.get_time() - self.clap_detector.time_at_clap
		else:
			return 60.0 # just return some large value

	def go_to(self, target):

		# Extract key info from input
		d = target[0] # Target in distorted coordinates
		range = target[1] # Range to target
		index = target[2] # Camera id

		# Convert distordet coordinates back into pixel coordinates
		p = self.vision.camera_model_full.d2p(d)

		#Convert pixel location to viewline from camera
		v = self.vision.camera_model_full.p2v(p)

		#Convert viewline to point in Head frame
		oh = self.vision.camera_model_full.v2oh(index, v, range)

		#Get location of nose tip fovea
		fov = miro.utils.get("LOC_SONAR_FOVEA_HEAD")

		#Calculate Vector from fovea to target
		vec = oh - fov

		while np.linalg.norm(vec) >= 0.1:
			#Calculate vector from fovea to target
			vec = oh - fov

			# Find pos of target in world frame
			ow = self.kc.changeFrameAbs(miro.constants.LINK_HEAD, miro.constants.LINK_WORLD, oh)

			#Construct push for link head using fovea
			self.msg_push.link = miro.constants.LINK_HEAD
			self.msg_push.flags = miro.constants.PUSH_FLAG_VELOCITY
			self.msg_push.pushpos = Vector3(miro.constants.LOC_NOSE_TIP_X, miro.constants.LOC_NOSE_TIP_Y, miro.constants.LOC_NOSE_TIP_Z)
			self.msg_push.pushvec = Vector3(vec[0], vec[1], vec[2])
			self.push_pub.publish(self.msg_push)

			#Construct push for kinematic chain model
			kc_push = miro.utils.kc.KinematicPush()
			kc_push.link = self.msg_push.link
			kc_push.flags = self.msg_push.flags
			kc_push.pos = np.array([miro.constants.LOC_NOSE_TIP_X, miro.constants.LOC_NOSE_TIP_Y, miro.constants.LOC_NOSE_TIP_Z])
			kc_push.vec = np.array([vec[0], vec[1], vec[2]])
			self.kc.push(kc_push)

			# Recalculate target in new head frame
			oh = self.kc.changeFrameAbs(miro.constants.LINK_WORLD, miro.constants.LINK_HEAD, ow)

			#print np.linalg.norm(vec)
			self.yield_cpu()

	def set_forward_speed(self, x):
		self.pause()
		x = np.clip(x, -miro.constants.WHEEL_MAX_SPEED_M_PER_S, miro.constants.WHEEL_MAX_SPEED_M_PER_S)
		self.velocity.twist.linear.x = x

	def set_turn_speed(self, z_deg):
		self.pause()
		z_rad = math.radians(z_deg)
		z_rad = np.clip(z_rad, -miro.constants.WHEEL_MAX_ANG_SPEED_RAD_PER_S, miro.constants.WHEEL_MAX_ANG_SPEED_RAD_PER_S)
		self.velocity.twist.angular.z = z_rad

	def step_drive(self, dist, speed=0.3):

		abs_speed = abs(speed)

		# Set direction
		if dist > 0.0:
			vel = abs_speed
		else:
			vel = -abs_speed

		# Get current location relative to start pose
		x = self.pose_controller.pose_est.x
		y = self.pose_controller.pose_est.y
		theta = self.pose_controller.pose_est.theta

		# Get target location relative to start pose
		target_x = x + np.cos(theta)*dist
		target_y = y + np.sin(theta)*dist

		# Calculate change in x and y required
		if target_x > 0:
			dx = target_x - x
		else:
			dx = x - target_x
		if target_y > 0:
			dy = target_y - y
		else:
			dy = y - target_y

		# Control to neary 0 to avoid overshoot and error
		while dx > 0.1 or dy > 0.1:
			time.sleep(0.1)
			self.set_forward_speed(vel)

			# #Iitialise Pose object
			# self.cmd_vel.zero()
			#
			# #Take commanded Velocity and pass to Pose Controller
			# self.cmd_vel.dr = self.velocity.twist.linear.x
			# self.cmd_vel.dtheta = self.velocity.twist.angular.z
			# adjusted_cmd_vel = self.pose_controller.command_velocity(self.cmd_vel, T=0.1)
			#
			# #Take adjusted velocity and publish to robot
			# self.adjusted_velocity.twist.linear.x = adjusted_cmd_vel.dr
			# self.adjusted_velocity.twist.angular.z = adjusted_cmd_vel.dtheta

			self.velocity_pub.publish(self.velocity)

			# Recalculate change in x and y required
			if target_x > 0:
				dx = target_x - self.pose_controller.pose_est.x
			else:
				dx = self.pose_controller.pose_est.x - target_x
			if target_y > 0:
				dy = target_y - self.pose_controller.pose_est.y
			else:
				dy = self.pose_controller.pose_est.y - target_y

		# Stop Driving
		self.set_forward_speed(0)

	def step_turn(self, deg):

		# Convert degrees to radians
		rad = math.radians(deg)

		# Set direction
		if rad < 0.0:
			clockwise = True
		else:
			clockwise = False

		#Get current Angle from Pose Controller
		start_ang = self.pose_controller.pose_est.theta

		#Calculate Target Angle
		target_ang = start_ang + rad

		if clockwise:
			d_ang = self.pose_controller.pose_est.theta - target_ang
			speed = -30
		else:
			d_ang = target_ang - self.pose_controller.pose_est.theta
			speed = 30

		# Turn until nearly 0 to prevent overshoot
		while d_ang > 0.05:
			self.pause()
			time.sleep(0.1)
			self.set_turn_speed(speed)
			self.velocity_pub.publish(self.velocity)
			if clockwise:
				d_ang = self.pose_controller.pose_est.theta - target_ang
			else:
				d_ang = target_ang - self.pose_controller.pose_est.theta

		# Stop turning
		self.set_turn_speed(0)

	def set_neck(self, joint_index, degrees):
		self.pause()
		if joint_index >= 1 and joint_index < 4:
			if joint_index == miro.constants.JOINT_LIFT:
				degrees = np.clip(degrees, 5, 60)
			elif joint_index == miro.constants.JOINT_PITCH:
				degrees = np.clip(degrees, -22, 8)
			elif joint_index == miro.constants.JOINT_YAW:
				degrees = np.clip(degrees, -60, 60)

			joint_radians = math.radians(degrees)
			self.kin_joints.position[joint_index] = joint_radians

	def set_joint(self, joint_index, pos):
		self.pause()
		if 0 <= joint_index < 6:
			pos = np.clip(pos, 0.0, 1.0)
			self.cos_joints.data[joint_index] = pos

	def wag_tail(self, rate):
		self.pause()
		if rate == 0:
			self.wag = False
		else:
			rate = np.clip(rate, 3, 20)
			self.wag_rate = rate
			self.wag = True

	def play_tone(self, audio_freq, audio_vol, audio_dur_secs):
		self.pause()
		audio_freq = np.clip(audio_freq, 200, 2000)
		audio_vol = np.clip(audio_vol, 0, 255)
		audio_dur = int(audio_dur_secs*50)
		self.tone.data[miro.constants.TONE_FREQ] = audio_freq
		self.tone.data[miro.constants.TONE_DUR] = audio_dur
		self.tone.data[miro.constants.TONE_VOL] = audio_vol
		self.audio_tone_pub.publish(self.tone)

	def control_led(self, led_pos, colour, brightness):
		self.pause()
		led_pos = np.clip(led_pos, 0, 5)
		brightness = np.clip(brightness, 0, 255)
		r = colour[0]
		g = colour[1]
		b = colour[2]
		led_value = (int(brightness) << 24) | (r << 16) | (g << 8) | b
		self.illum.data[led_pos] = led_value

	def sleep(self, dur):

		self.set_time_limit(self.get_time() + dur)

		# loop until time limit
		while self.wait_for_time_limit():

			# yields
			self.pause()
			self.yield_cpu()

	def start_timer(self, user_secs):
		self.pause()
		self.timer_end_time = self.get_time() + user_secs

	def timer(self):
		if self.get_time() < self.timer_end_time:
			self.yield_cpu()
			return True
		else:
			self.timer_end_time = 0.0
			return False

	def cam_left_callback(self, ros_image):
		self.vision.process(ros_image, 0)

	def cam_right_callback(self, ros_image):
		self.vision.process(ros_image, 1)

	def update(self):

		t_loop = 0.0

		# loop until exit() called AND not in a time limit loop
		while self.m_ready or self.time_limit:

			# wait for boundary
			if self.time_now < t_loop:

				# yield
				self.yield_cpu()

				# restart loop
				continue

			# check pause
			self.pause()

			#publish

			#Adjust velocity commands using Pose controller if enabled
			if self.pose_ctrl:

				#Iitialise Pose object
				self.cmd_vel.zero()

				#Take commanded Velocity and pass to Pose Controller
				self.cmd_vel.dr = self.velocity.twist.linear.x
				self.cmd_vel.dtheta = self.velocity.twist.angular.z
				adjusted_cmd_vel = self.pose_controller.command_velocity(self.cmd_vel, T=0.1)

				#Take adjusted velocity and publish to robot
				self.adjusted_velocity.twist.linear.x = adjusted_cmd_vel.dr
				self.adjusted_velocity.twist.angular.z = adjusted_cmd_vel.dtheta

				if self.velocity.twist.linear.x == 0.0:
					#Do not use pose_controller to control to 0 as noise causes infinite correction
					self.adjusted_velocity.twist.linear.x = 0.0
				if self.velocity.twist.angular.z == 0.0:
					#Do not use pose_controller to control to 0 as noise causes infinite correction
					self.adjusted_velocity.twist.angular.z = 0.0

				self.velocity_pub.publish(self.adjusted_velocity)

			#Else publish unadjusted velocites
			else:
				self.velocity_pub.publish(self.velocity)
				#self.velocity = TwistStamped() # velocities are zeroed after use

			# publish
			self.kinematic_joints_pub.publish(self.kin_joints)

			# Wag tail if neccessary
			if self.wag:
				# update tail position
				self.wag_phase += np.pi / self.wag_rate
				if self.wag_phase >= 2 * np.pi:
					self.wag_phase -= 2 * np.pi
				self.cos_joints.data[miro.constants.JOINT_WAG] = np.sin(self.wag_phase) * 0.5 + 0.5

			# publish
			self.cosmetic_joints_pub.publish(self.cos_joints)

			# publish
			self.illum_pub.publish(self.illum)

			# Change flag to allow user control loop to run
			self.updated = True

			# advance at 10Hz
			t_loop += 0.1

		# mark exit
		self.thread_running = False

	def ready(self):

		# wait for boundary
		while not self.updated:
			self.yield_cpu()

		# clear ready state
		self.updated = False

		# return ready state
		return self.m_ready

	def pause(self):

		# currently, we do not support pause
		pass

		"""
		#Time at start of pause
		pause_start = self.get_time()

		#Check for Pause Flag
		while (self.m_ready):
			# Check for presence of pause command
			if os.path.exists(FILE_WEB_CMD):
				with open(FILE_WEB_CMD, "r", os.O_NONBLOCK) as file:
					self.web_cmd = file.read()
					file.close()
			else:
				self.web_cmd = ""

			if self.web_cmd == "pause":
				self.pause_flag = True
			else:
				break

			time.sleep(0.1)

		#Calculate pause time
		if self.pause_flag:
			pause_time = self.get_time() - pause_start
			self.timer_end_time = self.timer_end_time + pause_time
			self.pause_flag = False
		"""

	def exit(self):

		# if currently in ready state
		if self.m_ready:

			# let thread exit
			self.m_ready = False

			# wait for it to do so (was "waiting for thread exit")
			print "[interface] disconnecting from robot...",
			while self.thread_running:
				time.sleep(0.1)
			print "OK"

			# disable all subs
			self.sensors_sub.unregister()
			self.touch_body_sub.unregister()
			self.touch_head_sub.unregister()
			self.mics_sub.unregister()
			self.cam_left_sub.unregister()
			self.cam_right_sub.unregister()

			# wait one second to hopefully catch any remaining
			# callbacks and avoid spurious error msgs at close
			time.sleep(1.0)
