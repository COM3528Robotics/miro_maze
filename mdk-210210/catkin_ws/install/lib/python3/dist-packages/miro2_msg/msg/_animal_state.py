# This Python file uses the following encoding: utf-8
"""autogenerated by genpy from miro2_msg/animal_state.msg. Do not edit."""
import codecs
import sys
python3 = True if sys.hexversion > 0x03000000 else False
import genpy
import struct

import miro2_msg.msg

class animal_state(genpy.Message):
  _md5sum = "02b89a84b06f59e91819662e7c3d6b0e"
  _type = "miro2_msg/animal_state"
  _has_header = False  # flag to mark the presence of a Header object
  _full_text = """#	@section COPYRIGHT
#	Copyright (C) 2021 Consequential Robotics Ltd
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
# the "animal_state" is the state of the animal aspects of the model
# which includes "affect" values for emotion (quickly changing) and
# mood (slowly changing) and a "sleep" value (also slowly changing),
# and the animal's estimate of time. this state may also include, in
# future, physical states such as temperature.

#	DOCLINK ANIMAL STATE FLAGS
#
#	Some flags are included here because parts of the implementation
#	are in separate nodes that read this topic in order to determine
#	how they should behave, and their behaviour is affected by flags.
#
#	The values of these flags are defined in miro2.constants.
uint32 flags

# affective states
affect emotion
affect mood

# sleep state
sleep sleep

# normalised time of day (0.0 -> 1.0)
float32 time_of_day

# normalised ambient sound level (0.0 -> 1.0); when this is low or
# zero, the voice produced is at the reference level; when this is
# higher, the volume of the voice is increased so it can be heard.
# this is not a direct volume control.
#
# < 0.01 : pretty quiet
# 0.01 : normal ambient music
# 0.02-0.03 : loud music
# 0.05 : very loud music
# > 0.1 : System of a Down
float32 sound_level


================================================================================
MSG: miro2_msg/affect
#	@section COPYRIGHT
#	Copyright (C) 2021 Consequential Robotics Ltd
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
#	The "affect" state is two-dimensional, encoding valence
#	(0.0 = sad, 1.0 = happy) and arousal (0.0 = relaxed, 1.0 = alert).
#	The states are usually driven by signals entering the robot's
#	sensory systems, but can also be driven directly by other systems.

float32 valence
float32 arousal


================================================================================
MSG: miro2_msg/sleep
#	@section COPYRIGHT
#	Copyright (C) 2021 Consequential Robotics Ltd
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
#	The "sleep" state is two-dimensional, encoding "wakefulness"
#	(0.0 to 1.0, what it sounds like) and "pressure" (0.0 to 1.0,
#	tendency to move towards reduced wakefulness). The two states
#	evolve together to implement a relaxation oscillator.

float32 wakefulness
float32 pressure

"""
  __slots__ = ['flags','emotion','mood','sleep','time_of_day','sound_level']
  _slot_types = ['uint32','miro2_msg/affect','miro2_msg/affect','miro2_msg/sleep','float32','float32']

  def __init__(self, *args, **kwds):
    """
    Constructor. Any message fields that are implicitly/explicitly
    set to None will be assigned a default value. The recommend
    use is keyword arguments as this is more robust to future message
    changes.  You cannot mix in-order arguments and keyword arguments.

    The available fields are:
       flags,emotion,mood,sleep,time_of_day,sound_level

    :param args: complete set of field values, in .msg order
    :param kwds: use keyword arguments corresponding to message field names
    to set specific fields.
    """
    if args or kwds:
      super(animal_state, self).__init__(*args, **kwds)
      # message fields cannot be None, assign default values for those that are
      if self.flags is None:
        self.flags = 0
      if self.emotion is None:
        self.emotion = miro2_msg.msg.affect()
      if self.mood is None:
        self.mood = miro2_msg.msg.affect()
      if self.sleep is None:
        self.sleep = miro2_msg.msg.sleep()
      if self.time_of_day is None:
        self.time_of_day = 0.
      if self.sound_level is None:
        self.sound_level = 0.
    else:
      self.flags = 0
      self.emotion = miro2_msg.msg.affect()
      self.mood = miro2_msg.msg.affect()
      self.sleep = miro2_msg.msg.sleep()
      self.time_of_day = 0.
      self.sound_level = 0.

  def _get_types(self):
    """
    internal API method
    """
    return self._slot_types

  def serialize(self, buff):
    """
    serialize message into buffer
    :param buff: buffer, ``StringIO``
    """
    try:
      _x = self
      buff.write(_get_struct_I8f().pack(_x.flags, _x.emotion.valence, _x.emotion.arousal, _x.mood.valence, _x.mood.arousal, _x.sleep.wakefulness, _x.sleep.pressure, _x.time_of_day, _x.sound_level))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize(self, str):
    """
    unpack serialized message in str into this message instance
    :param str: byte array of serialized message, ``str``
    """
    if sys.version_info >= (3,0): codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      if self.emotion is None:
        self.emotion = miro2_msg.msg.affect()
      if self.mood is None:
        self.mood = miro2_msg.msg.affect()
      if self.sleep is None:
        self.sleep = miro2_msg.msg.sleep()
      end = 0
      _x = self
      start = end
      end += 36
      (_x.flags, _x.emotion.valence, _x.emotion.arousal, _x.mood.valence, _x.mood.arousal, _x.sleep.wakefulness, _x.sleep.pressure, _x.time_of_day, _x.sound_level,) = _get_struct_I8f().unpack(str[start:end])
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill


  def serialize_numpy(self, buff, numpy):
    """
    serialize message with numpy array types into buffer
    :param buff: buffer, ``StringIO``
    :param numpy: numpy python module
    """
    try:
      _x = self
      buff.write(_get_struct_I8f().pack(_x.flags, _x.emotion.valence, _x.emotion.arousal, _x.mood.valence, _x.mood.arousal, _x.sleep.wakefulness, _x.sleep.pressure, _x.time_of_day, _x.sound_level))
    except struct.error as se: self._check_types(struct.error("%s: '%s' when writing '%s'" % (type(se), str(se), str(locals().get('_x', self)))))
    except TypeError as te: self._check_types(ValueError("%s: '%s' when writing '%s'" % (type(te), str(te), str(locals().get('_x', self)))))

  def deserialize_numpy(self, str, numpy):
    """
    unpack serialized message in str into this message instance using numpy for array types
    :param str: byte array of serialized message, ``str``
    :param numpy: numpy python module
    """
    if sys.version_info >= (3,0): codecs.lookup_error("rosmsg").msg_type = self._type
    try:
      if self.emotion is None:
        self.emotion = miro2_msg.msg.affect()
      if self.mood is None:
        self.mood = miro2_msg.msg.affect()
      if self.sleep is None:
        self.sleep = miro2_msg.msg.sleep()
      end = 0
      _x = self
      start = end
      end += 36
      (_x.flags, _x.emotion.valence, _x.emotion.arousal, _x.mood.valence, _x.mood.arousal, _x.sleep.wakefulness, _x.sleep.pressure, _x.time_of_day, _x.sound_level,) = _get_struct_I8f().unpack(str[start:end])
      return self
    except struct.error as e:
      raise genpy.DeserializationError(e)  # most likely buffer underfill

_struct_I = genpy.struct_I
def _get_struct_I():
    global _struct_I
    return _struct_I
_struct_I8f = None
def _get_struct_I8f():
    global _struct_I8f
    if _struct_I8f is None:
        _struct_I8f = struct.Struct("<I8f")
    return _struct_I8f