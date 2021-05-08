// Generated by gencpp from file miro2_msg/animal_adjust.msg
// DO NOT EDIT!


#ifndef MIRO2_MSG_MESSAGE_ANIMAL_ADJUST_H
#define MIRO2_MSG_MESSAGE_ANIMAL_ADJUST_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <miro2_msg/affect_adjust.h>
#include <miro2_msg/affect_adjust.h>
#include <miro2_msg/sleep_adjust.h>

namespace miro2_msg
{
template <class ContainerAllocator>
struct animal_adjust_
{
  typedef animal_adjust_<ContainerAllocator> Type;

  animal_adjust_()
    : mood()
    , emotion()
    , sleep()  {
    }
  animal_adjust_(const ContainerAllocator& _alloc)
    : mood(_alloc)
    , emotion(_alloc)
    , sleep(_alloc)  {
  (void)_alloc;
    }



   typedef  ::miro2_msg::affect_adjust_<ContainerAllocator>  _mood_type;
  _mood_type mood;

   typedef  ::miro2_msg::affect_adjust_<ContainerAllocator>  _emotion_type;
  _emotion_type emotion;

   typedef  ::miro2_msg::sleep_adjust_<ContainerAllocator>  _sleep_type;
  _sleep_type sleep;





  typedef boost::shared_ptr< ::miro2_msg::animal_adjust_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::miro2_msg::animal_adjust_<ContainerAllocator> const> ConstPtr;

}; // struct animal_adjust_

typedef ::miro2_msg::animal_adjust_<std::allocator<void> > animal_adjust;

typedef boost::shared_ptr< ::miro2_msg::animal_adjust > animal_adjustPtr;
typedef boost::shared_ptr< ::miro2_msg::animal_adjust const> animal_adjustConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::miro2_msg::animal_adjust_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::miro2_msg::animal_adjust_<ContainerAllocator> >::stream(s, "", v);
return s;
}


template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator==(const ::miro2_msg::animal_adjust_<ContainerAllocator1> & lhs, const ::miro2_msg::animal_adjust_<ContainerAllocator2> & rhs)
{
  return lhs.mood == rhs.mood &&
    lhs.emotion == rhs.emotion &&
    lhs.sleep == rhs.sleep;
}

template<typename ContainerAllocator1, typename ContainerAllocator2>
bool operator!=(const ::miro2_msg::animal_adjust_<ContainerAllocator1> & lhs, const ::miro2_msg::animal_adjust_<ContainerAllocator2> & rhs)
{
  return !(lhs == rhs);
}


} // namespace miro2_msg

namespace ros
{
namespace message_traits
{





template <class ContainerAllocator>
struct IsMessage< ::miro2_msg::animal_adjust_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::miro2_msg::animal_adjust_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::miro2_msg::animal_adjust_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::miro2_msg::animal_adjust_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::miro2_msg::animal_adjust_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::miro2_msg::animal_adjust_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::miro2_msg::animal_adjust_<ContainerAllocator> >
{
  static const char* value()
  {
    return "b26581aa1bf2879431400970feb511a2";
  }

  static const char* value(const ::miro2_msg::animal_adjust_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xb26581aa1bf28794ULL;
  static const uint64_t static_value2 = 0x31400970feb511a2ULL;
};

template<class ContainerAllocator>
struct DataType< ::miro2_msg::animal_adjust_<ContainerAllocator> >
{
  static const char* value()
  {
    return "miro2_msg/animal_adjust";
  }

  static const char* value(const ::miro2_msg::animal_adjust_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::miro2_msg::animal_adjust_<ContainerAllocator> >
{
  static const char* value()
  {
    return "#	@section COPYRIGHT\n"
"#	Copyright (C) 2021 Consequential Robotics Ltd\n"
"#	\n"
"#	@section AUTHOR\n"
"#	Consequential Robotics http://consequentialrobotics.com\n"
"#	\n"
"#	@section LICENSE\n"
"#	For a full copy of the license agreement, and a complete\n"
"#	definition of \"The Software\", see LICENSE in the MDK root\n"
"#	directory.\n"
"#	\n"
"#	Subject to the terms of this Agreement, Consequential\n"
"#	Robotics grants to you a limited, non-exclusive, non-\n"
"#	transferable license, without right to sub-license, to use\n"
"#	\"The Software\" in accordance with this Agreement and any\n"
"#	other written agreement with Consequential Robotics.\n"
"#	Consequential Robotics does not transfer the title of \"The\n"
"#	Software\" to you; the license granted to you is not a sale.\n"
"#	This agreement is a binding legal agreement between\n"
"#	Consequential Robotics and the purchasers or users of \"The\n"
"#	Software\".\n"
"#	\n"
"#	THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY\n"
"#	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE\n"
"#	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR\n"
"#	PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS\n"
"#	OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR\n"
"#	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR\n"
"#	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\n"
"#	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
"#	\n"
"#\n"
"#	Animal adjust provides a route for directly adjusting the\n"
"#	animal state. See message \"animal_state\" for a description\n"
"#	of the state itself; see message \"adjust\" for details of\n"
"#	how adjustment can be performed.\n"
"\n"
"affect_adjust mood\n"
"affect_adjust emotion\n"
"sleep_adjust sleep\n"
"\n"
"\n"
"================================================================================\n"
"MSG: miro2_msg/affect_adjust\n"
"#	@section COPYRIGHT\n"
"#	Copyright (C) 2021 Consequential Robotics Ltd\n"
"#	\n"
"#	@section AUTHOR\n"
"#	Consequential Robotics http://consequentialrobotics.com\n"
"#	\n"
"#	@section LICENSE\n"
"#	For a full copy of the license agreement, and a complete\n"
"#	definition of \"The Software\", see LICENSE in the MDK root\n"
"#	directory.\n"
"#	\n"
"#	Subject to the terms of this Agreement, Consequential\n"
"#	Robotics grants to you a limited, non-exclusive, non-\n"
"#	transferable license, without right to sub-license, to use\n"
"#	\"The Software\" in accordance with this Agreement and any\n"
"#	other written agreement with Consequential Robotics.\n"
"#	Consequential Robotics does not transfer the title of \"The\n"
"#	Software\" to you; the license granted to you is not a sale.\n"
"#	This agreement is a binding legal agreement between\n"
"#	Consequential Robotics and the purchasers or users of \"The\n"
"#	Software\".\n"
"#	\n"
"#	THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY\n"
"#	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE\n"
"#	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR\n"
"#	PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS\n"
"#	OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR\n"
"#	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR\n"
"#	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\n"
"#	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
"#	\n"
"\n"
"adjust valence\n"
"adjust arousal\n"
"\n"
"\n"
"================================================================================\n"
"MSG: miro2_msg/adjust\n"
"#	@section COPYRIGHT\n"
"#	Copyright (C) 2021 Consequential Robotics Ltd\n"
"#	\n"
"#	@section AUTHOR\n"
"#	Consequential Robotics http://consequentialrobotics.com\n"
"#	\n"
"#	@section LICENSE\n"
"#	For a full copy of the license agreement, and a complete\n"
"#	definition of \"The Software\", see LICENSE in the MDK root\n"
"#	directory.\n"
"#	\n"
"#	Subject to the terms of this Agreement, Consequential\n"
"#	Robotics grants to you a limited, non-exclusive, non-\n"
"#	transferable license, without right to sub-license, to use\n"
"#	\"The Software\" in accordance with this Agreement and any\n"
"#	other written agreement with Consequential Robotics.\n"
"#	Consequential Robotics does not transfer the title of \"The\n"
"#	Software\" to you; the license granted to you is not a sale.\n"
"#	This agreement is a binding legal agreement between\n"
"#	Consequential Robotics and the purchasers or users of \"The\n"
"#	Software\".\n"
"#	\n"
"#	THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY\n"
"#	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE\n"
"#	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR\n"
"#	PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS\n"
"#	OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR\n"
"#	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR\n"
"#	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\n"
"#	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
"#	\n"
"#\n"
"#	Adjust message provides a route for directly adjusting\n"
"#	a state of the biomimetic model. There are two ways to\n"
"#	specify an adjustment, selected independently for each\n"
"#	adjustment channel.\n"
"#\n"
"#	1) Provide a target value in \"data\" and a \"gamma\" value\n"
"#	between 0 and 1 to cause the state to approach the target:\n"
"#\n"
"#	(at 50Hz)\n"
"#	state += gamma * (data - state)\n"
"#\n"
"#	2) Provide a delta value in \"data\" and set \"gamma\"\n"
"#	to -1 to indicate this drive mode:\n"
"#\n"
"#	(at 50Hz)\n"
"#	state += data\n"
"#\n"
"#	Understood values of gamma, therefore, are:\n"
"#	   -1 : add \"data\" to state\n"
"#	    0 : do nothing\n"
"#	  0-1 : move state towards \"data\"\n"
"#	    1 : instantly set state to \"data\"\n"
"\n"
"float32 data\n"
"float32 gamma\n"
"\n"
"\n"
"================================================================================\n"
"MSG: miro2_msg/sleep_adjust\n"
"#	@section COPYRIGHT\n"
"#	Copyright (C) 2021 Consequential Robotics Ltd\n"
"#	\n"
"#	@section AUTHOR\n"
"#	Consequential Robotics http://consequentialrobotics.com\n"
"#	\n"
"#	@section LICENSE\n"
"#	For a full copy of the license agreement, and a complete\n"
"#	definition of \"The Software\", see LICENSE in the MDK root\n"
"#	directory.\n"
"#	\n"
"#	Subject to the terms of this Agreement, Consequential\n"
"#	Robotics grants to you a limited, non-exclusive, non-\n"
"#	transferable license, without right to sub-license, to use\n"
"#	\"The Software\" in accordance with this Agreement and any\n"
"#	other written agreement with Consequential Robotics.\n"
"#	Consequential Robotics does not transfer the title of \"The\n"
"#	Software\" to you; the license granted to you is not a sale.\n"
"#	This agreement is a binding legal agreement between\n"
"#	Consequential Robotics and the purchasers or users of \"The\n"
"#	Software\".\n"
"#	\n"
"#	THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY\n"
"#	KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE\n"
"#	WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR\n"
"#	PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS\n"
"#	OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR\n"
"#	OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR\n"
"#	OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE\n"
"#	SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\n"
"#	\n"
"\n"
"adjust wakefulness\n"
"adjust pressure\n"
"\n"
;
  }

  static const char* value(const ::miro2_msg::animal_adjust_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::miro2_msg::animal_adjust_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.mood);
      stream.next(m.emotion);
      stream.next(m.sleep);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct animal_adjust_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::miro2_msg::animal_adjust_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::miro2_msg::animal_adjust_<ContainerAllocator>& v)
  {
    s << indent << "mood: ";
    s << std::endl;
    Printer< ::miro2_msg::affect_adjust_<ContainerAllocator> >::stream(s, indent + "  ", v.mood);
    s << indent << "emotion: ";
    s << std::endl;
    Printer< ::miro2_msg::affect_adjust_<ContainerAllocator> >::stream(s, indent + "  ", v.emotion);
    s << indent << "sleep: ";
    s << std::endl;
    Printer< ::miro2_msg::sleep_adjust_<ContainerAllocator> >::stream(s, indent + "  ", v.sleep);
  }
};

} // namespace message_operations
} // namespace ros

#endif // MIRO2_MSG_MESSAGE_ANIMAL_ADJUST_H
