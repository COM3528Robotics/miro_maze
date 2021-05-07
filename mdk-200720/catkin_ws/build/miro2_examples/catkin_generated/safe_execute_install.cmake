execute_process(COMMAND "/home/student/mdk-200720/catkin_ws/build/miro2_examples/catkin_generated/python_distutils_install.sh" RESULT_VARIABLE res)

if(NOT res EQUAL 0)
  message(FATAL_ERROR "execute_process(/home/student/mdk-200720/catkin_ws/build/miro2_examples/catkin_generated/python_distutils_install.sh) returned error code ")
endif()
