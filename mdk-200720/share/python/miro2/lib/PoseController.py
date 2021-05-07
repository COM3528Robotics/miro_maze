#!/usr/bin/python
#
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

import math
import numpy as np

import miro2 as miro

# this controller operates by trying to keep a notional "fovea"
# in the location it is expected to be in if the robot moved
# exactly as commanded. using a fovea, which is separated from
# the axis of rotation, avoids the singularity around small
# errors near the rotational axis, at the cost of somewhat
# modified behaviour for large errors. some balance between
# these concerns is provided through the parameter "foveal_dist".
#
# the controller can be used in different modes. most simply,
# after initialisation, pass wheel_speed reports from the opto
# encoders in using update_sensors(), desired movements through
# command_velocity(), and pass the return value from that down
# to control/cmd_vel.
#
# alternatively, if you wish to use a separate motion planning
# model, you can call command_position() directly and pass its
# return value to control/cmd_vel.

class PoseController:

	def __init__(self):
	
		# parameters
		self.foveal_dist = 0.2
		self.buffer_len = 10
		self.gain_r = 4.0
		self.gain_theta = 7.0
	
		# controller estimate of pose in WORLD
		self.pose_est = miro.lib.Pose()

		# target pose in WORLD		
		self.pose_tgt = miro.lib.Pose()

		# spread gain forward in time a bit because controller
		# will tend to be behind the physical world and this
		# helps it to stay fairly well up to date with requests.
		self.gains = np.array([0.0] * self.buffer_len)

	def update_sensors(self, wheel_speed, T = miro.constants.PLATFORM_TICK_SEC):
	
		# convert from speed to delta
		wheel_speed *= T

		# convert to dr/dtheta
		body_vel = miro.utils.wheel_speed2pose_vel(wheel_speed)
		
		# update estimate of pose
		self.pose_est.update(body_vel)
		
	def command_position(self, pose_tgt, master_gain = 1.0):
	
		# call this function to provide the target model and
		# return the controlled velocity (with specified gain).
	
		# compute target fovea location
		xt = pose_tgt.x + np.cos(pose_tgt.theta) * self.foveal_dist
		yt = pose_tgt.y + np.sin(pose_tgt.theta) * self.foveal_dist
		
		# map that into egocentric space
		(xte, yte) = self.pose_est.egocentric(xt, yt)
		
		# find error from target fovea location
		xe = xte - self.foveal_dist
		ye = yte - 0.0

		# handle control lag
		self.gains = np.append(self.gains, master_gain)[1:]
		master_gain = np.max(self.gains)
	
		# do control (gains are very rough...)
		dr = xe * self.gain_r * master_gain
		dtheta = ye / self.foveal_dist * self.gain_theta * master_gain
		
		# return controlled velocity
		return miro.lib.DeltaPose(dr, dtheta)

	def command_velocity(self, cmd_vel, T = miro.constants.PLATFORM_TICK_SEC, master_gain = 1.0):
	
		# call this function to move the target model for T
		# seconds with the specified desired velocity, and
		# return the controlled velocity (with specified gain).
	
		# drive target pose
		dpose = miro.lib.DeltaPose(cmd_vel.dr * T, cmd_vel.dtheta * T)
		self.pose_tgt.update(dpose)

		# run controller
		return self.command_position(self.pose_tgt, master_gain)

