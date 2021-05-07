#!/bin/sh

if [ -n "$DESTDIR" ] ; then
    case $DESTDIR in
        /*) # ok
            ;;
        *)
            /bin/echo "DESTDIR argument must be absolute... "
            /bin/echo "otherwise python's distutils will bork things."
            exit 1
    esac
fi

echo_and_run() { echo "+ $@" ; "$@" ; }

echo_and_run cd "/home/student/mdk/catkin_ws/src/miro2_msg"

# ensure that Python install destination exists
echo_and_run mkdir -p "$DESTDIR/home/student/mdk/catkin_ws/install/lib/python2.7/dist-packages"

# Note that PYTHONPATH is pulled from the environment to support installing
# into one location when some dependencies were installed in another
# location, #123.
echo_and_run /usr/bin/env \
    PYTHONPATH="/home/student/mdk/catkin_ws/install/lib/python2.7/dist-packages:/home/student/mdk-200720/catkin_ws/build/lib/python2.7/dist-packages:$PYTHONPATH" \
    CATKIN_BINARY_DIR="/home/student/mdk-200720/catkin_ws/build" \
    "/usr/bin/python2" \
    "/home/student/mdk/catkin_ws/src/miro2_msg/setup.py" \
     \
    build --build-base "/home/student/mdk-200720/catkin_ws/build/miro2_msg" \
    install \
    --root="${DESTDIR-/}" \
    --install-layout=deb --prefix="/home/student/mdk/catkin_ws/install" --install-scripts="/home/student/mdk/catkin_ws/install/bin"
