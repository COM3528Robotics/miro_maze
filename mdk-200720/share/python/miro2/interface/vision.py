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
#
# https://pypi.org/project/apriltag/

import time
import os
import numpy as np
import cv2
import rospy
from cv_bridge import CvBridge, CvBridgeError
from sensor_msgs.msg import CompressedImage, Image
import apriltag
import miro2 as miro

class Vision:
	def __init__(self):

		self.image_converter = CvBridge()

		self.cam_images = [None, None]
		self.ann_images = [None, None]
		self.frame_w = None
		self.frame_h = None
		self.x_cent = None
		self.y_cent = None

		self.found_circle = [None, None]
		self.circle_str = [None, None]

		self.topic_root = '/' + os.getenv("MIRO_ROBOT_NAME") + '/'
		self.ann_image_pub_l = rospy.Publisher(self.topic_root + "sensors/cam_l/annotated", Image, queue_size=0)
		self.ann_image_pub_r = rospy.Publisher(self.topic_root + "sensors/cam_r/annotated", Image, queue_size=0)

		april_options = apriltag.DetectorOptions( \
				families='tag16h5',
				border=1,
				nthreads=4,
				quad_decimate=1.0,
				quad_blur=0.0,
				refine_edges=True,
				refine_decode=False,
				refine_pose=False,
				debug=False,
				quad_contours=True)

		self.camera_model_full=None
		self.april_detector = apriltag.Detector(april_options)
		self.tag = miro.msg.object_tag()

		#Generate constants for calculating distance
		#Using formula F = (P*D)/W
		#Where F = "Focal Length", P = Percived Width, D = Distance, W = Width
		#Previous calibration with cube at 0.5m, and Width = 0.057m shows P = 0.0583887183
		#Therefore: F = (0.0583887183 * 0.5)/0.057 = 0.512181739
		self.april_F = 0.512181739
		self.april_FW = 0.057

	def process(self, img_data, index):
		try:
			cam_image = self.image_converter.compressed_imgmsg_to_cv2(img_data, "bgr8")
		except CvBridgeError as e:
			print("Conversion of image failed \n")
			print(e)

		if self.camera_model_full is None:
			self.camera_model_full = miro.utils.camera_model.CameraModel()
			self.camera_model_full.set_frame_size_from_img(cam_image)

		if self.frame_w is None:
			im_h, im_w = cam_image.shape[:2]
			self.frame_w, self.frame_h = im_w, im_h
			self.x_cent = self.frame_w / 2.0
			self.y_cent = self.frame_h / 2.0

		self.cam_images[index] = cam_image

		# currently we don't do annotate
		return

		self.annotate(index)
		self.publish(index)

	def annotate(self, index):
		self.ann_images[index] = self.cam_images[index].copy()
		cv2.line(self.ann_images[index], (int(round(self.x_cent)), 0), (int(round(self.x_cent)), self.frame_h), (0, 0, 0), 4)
		cv2.line(self.ann_images[index], (0, int(round(self.y_cent))), (self.frame_w, int(round(self.y_cent))), (0, 0, 0), 4)
		cv2.line(self.ann_images[index], (int(round(self.x_cent)), 0), (int(round(self.x_cent)), self.frame_h), (255, 255, 255), 2)
		cv2.line(self.ann_images[index], (0, int(round(self.y_cent))), (self.frame_w, int(round(self.y_cent))), (255, 255, 255), 2)

		if not self.found_circle[index] is None:
			cv2.circle(self.ann_images[index], (self.found_circle[index][0], self.found_circle[index][1]), self.found_circle[index][2], (0, 255, 0), 2)
			cv2.circle(self.ann_images[index], (self.found_circle[index][0], self.found_circle[index][1]), 1, (0, 255, 0), 2)

			text_y_offset = 22
			for i, line in enumerate(self.circle_str[index].split(",")):
				text_y = self.found_circle[index][1] - text_y_offset + i*text_y_offset
				cv2.putText(self.ann_images[index], line, (self.found_circle[index][0]+5, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 6)
				cv2.putText(self.ann_images[index], line, (self.found_circle[index][0]+5, text_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

	def clear(self, index):
		self.found_circle[index] = None

	def publish(self, index):
		if index == 0:
			self.ann_image_pub_l.publish(self.image_converter.cv2_to_imgmsg(self.ann_images[0], "bgr8"))
		else:
			self.ann_image_pub_r.publish(self.image_converter.cv2_to_imgmsg(self.ann_images[1], "bgr8"))

	def rgb_to_hsv(self, colour):
		#create colour code from user selected colour
		bgr_colour = np.uint8([[[colour[2], colour[1], colour[0]]]])
		hsv_colour = cv2.cvtColor(bgr_colour, cv2.COLOR_BGR2HSV)
		hue = hsv_colour[0,0][0]
		return hue

	def colour_mask(self, im, hue, hue_range):

		#convert image to hsv colour space
		im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

		# mask image
		hue_min = hue - hue_range
		hue_max = hue + hue_range

		if hue_min < 0:
			lo = np.array([0, 70, 70])
			hi = np.array([hue_max, 255, 255])
			mask1 = cv2.inRange(im_hsv, lo, hi)
			lo = np.array([hue_min + 180, 70, 70])
			hi = np.array([180, 255, 255])
			mask2 = cv2.inRange(im_hsv, lo, hi)
			mask = cv2.bitwise_or(mask1, mask2)
			return mask
		elif hue_max > 180:
			lo = np.array([hue_min, 70, 70])
			hi = np.array([180, 255, 255])
			mask1 = cv2.inRange(im_hsv, lo, hi)
			lo = np.array([0, 70, 70])
			hi = np.array([hue_max-180, 255, 255])
			mask2 = cv2.inRange(im_hsv, lo, hi)
			mask = cv2.bitwise_or(mask1, mask2)
			return mask
		else:
			lo = np.array([hue_min, 70, 70])
			hi = np.array([hue_max, 255, 255])
			mask = cv2.inRange(im_hsv, lo, hi)
			return mask

	def calc_com(self, rgb, index):

		# get image
		im = self.cam_images[index]
		if im is None:
			return None

		com = [[None, None], None]

		#Convert string to hsv colur value
		hue = self.rgb_to_hsv(rgb)

		# define hue range
		huer = 30

		#filter image for specified colour
		mask = self.colour_mask(im, hue, huer)

		#Count number of matching pxels
		matching_pix = np.sum(mask == 255)

		com[1] = matching_pix

		if matching_pix != 0:
			# calculate x,y coordinate of center
			moments = cv2.moments(mask, True)
			cX = int(moments["m10"] / moments["m00"])
			cY = int(moments["m01"] / moments["m00"])
			p = [cX, cY]
			com[0] = self.camera_model_full.p2d(p)

		return com

	def detect_shapes(self, rgb, vert, index):

		# get image
		im = self.cam_images[index]
		if im is None:
			return None

		shape = [[None, None], 0]
		#Convert string to hsv colur value
		hue = self.rgb_to_hsv(rgb)

		# define hue range
		huer = 15

		#filter image for specified colour
		mask = self.colour_mask(im, hue, huer)

		#find contours in image
		_, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		if len(contours) == 0:
			return None
		else:
			for contour in contours:
				M = cv2.moments(contour)
				if M["m00"] != 0:
					cX = int((M["m10"] / M["m00"]))
					cY = int((M["m01"] / M["m00"]))
					peri = cv2.arcLength(contour, True)
					approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
					if len(approx) == vert:
						area = cv2.contourArea(contour)
						if area > shape[1]:
							shape[1] = area
							p = [cX, cY]
							shape[0] = self.camera_model_full.p2d(p)
			if shape[0] == None:
				return None
			else:
				return shape

	def detect_april(self, index):

		# get image
		im = self.cam_images[index]
		if im is None:
			return None, None

		#Convert Image to greyscale
		im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

		#Detect Tags
		result = self.april_detector.detect(im)

		#Reset tag size
		max_distance = 0.0
		distance = None

		if len(result) > 0:
			count = 0
			for i in range(len(result)):
				tag = result[i]

				id = tag[1]
				ham = tag[2]

				# pare by id and hamming distance
				if ham == 0 and id >= 1 and id <= 6:

					count += 1

					# extract fields
					family = tag[0]
					id = tag[1]
					goodness = tag[3]
					decmar = tag[4]
					hom = tag[5]
					cen = tag[6]
					corn = tag[7]

					# convert to d
					cen_d = self.camera_model_full.p2d(cen)
					corn_d = corn
					for i in range(4):
						corn_d[i] = self.camera_model_full.p2d(corn_d[i])

					# flatten
					corn_d = corn_d.flatten()

					c = np.array(corn_d).reshape((4, 2))
					max_length = 0.0
					for i in range(4):
						if i == 3:
							j = 0
						else:
							j = i + 1
						length = np.sqrt(((c[i][0]-c[j][0])**2)+((c[i][1]-c[j][1])**2))
						if length > max_length:
							max_length = length

		            #Calculate DISTANCE
		            #Using formula F = (P*D)/W
		            #Where F = "Focal Length", P = Percived Width, D = Distance, W = Width
		            #Previous calibration with cube at 0.5m, and Width = 0.057m shows P = 0.0583887183
		            #Therefore: F = (0.0583887183 * 0.5)/0.057 = 0.512181739
		            #D = (F*W)/P
		            #F*W is constant as size of cube is constant
					if max_length > 0.0:
						distance = self.april_FW/max_length

					if distance > max_distance:
						max_distance = distance
						self.tag.conf = goodness
						self.tag.id = id
						self.tag.centre = cen_d
						self.tag.corners = corn_d

			if max_distance > 0.0:
				return self.tag, max_distance
			else:
				return None, None

		else:
			return None, None

	def detect_april_both(self):
		left_april, l_dist = self.detect_april(0)
		right_april, r_dist = self.detect_april(1)
		if left_april is None and right_april is None:
			return None, None, None
		elif left_april is None and right_april is not None:
			return right_april, r_dist, 1
		elif left_april is not None and right_april is None:
			return left_april, l_dist, 0
		else:
			if r_dist > l_dist:
				return right_april, r_dist, 1
			else:
				return left_april, l_dist, 0

	def calc_centre_colour(self, size, index):

		# get image
		im = self.cam_images[index]
		if im is None:
			return None

		if size == 1:
			roi_pix = im[int(self.y_cent), int(self.x_cent)]
			blue = roi_pix[0]
			green = roi_pix[1]
			red = roi_pix[2]
		elif size > 1:
			size = np.sqrt(size)
			roi_pix = im[int((self.frame_h - size)/2) : int((self.frame_h + size)/2), int((self.frame_w - size)/2) : int((self.frame_w + size)/2)]
			blue = np.mean(roi_pix[:, :, 0])
			green = np.mean(roi_pix[:, :, 1])
			red = np.mean(roi_pix[:, :, 2])
		else:
			blue = np.mean(im[:, :, 0])
			green = np.mean(im[:, :, 1])
			red = np.mean(im[:, :, 2])

		colour = [int(red), int(green), int(blue)]
		return colour


	def detect_ball(self, rgb, index):

		# get image
		im = self.cam_images[index]
		if im is None:
			return None

		# get image in HSV format
		im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

		#create colour code from user selected colour
		hue = self.rgb_to_hsv(rgb)

		# define hue range
		huer = 30

		#filter image for specified colour
		mask = self.colour_mask(im, hue, huer)

		# debug
		#cv2.imshow('im', mask)
		#cv2.waitKey(1)

		# clean up
		seg = mask
		seg = cv2.GaussianBlur(seg, (5, 5), 0)
		seg = cv2.erode(seg, None, iterations=2)
		seg = cv2.dilate(seg, None, iterations=2)

		# parameters
		canny_high_thresh = 128 # don't think it matters much for binary image, but does affect our grey image
		ball_detect_sensitivity = 20 # was 33 in Tom's code, lower detects more circles, so it's a trade-off
		ball_detect_min_dist_between_cens = 40 # was 40 in Tom's code, arbitrary
		ball_detect_min_radius = 5 # arbitrary, empirical, too small and we'll pick up noise objects
		ball_detect_max_radius = 60 # arbitrary, empirical

		# get circles
		circles = cv2.HoughCircles(seg, cv2.HOUGH_GRADIENT,
				1, ball_detect_min_dist_between_cens, \
				param1=canny_high_thresh, param2=ball_detect_sensitivity, \
				minRadius=ball_detect_min_radius, maxRadius=0)

		# Get largest circle
		max_circle = None
		#max_circle_norm = [None, None, None]
		if circles is not None:
			self.max_rad = 0
			circles = np.uint16(np.around(circles))

			for c in circles[0,:]:

				# annotate
				#cv2.circle(seg, (c[0], c[1]), c[2], (0, 255, 0), 2)

				if c[2] > self.max_rad:
					self.max_rad = c[2]
					max_circle = c

					"""
					max_circle_norm[0] = int(round(((max_circle[0] - self.x_cent) / self.x_cent) * 100.0))
					max_circle_norm[1] = int(round(-((max_circle[1] - self.y_cent) / self.y_cent) * 100.0))
					max_circle_norm[2] = int(round((max_circle[2]/self.x_cent)*100.0))
					"""

			self.found_circle[index] = max_circle
			#self.circle_str[index] = "x: " + str(max_circle_norm[0]) + "," + "y: " + str(max_circle_norm[1]) + "," + "r: " + str(max_circle_norm[2])

			if not max_circle is None:
				max_circle = np.array(max_circle).astype('float32')
				p = [max_circle[0], max_circle[1]]
				cen_d = self.camera_model_full.p2d(p)
				rad = max_circle[2]
				return [cen_d, rad]

			return None

		else:
			return None
