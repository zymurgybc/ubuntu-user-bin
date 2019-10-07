#!/bin/bash
# --------------------------------------------------------
# https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/
# --------------------------------------------------------

echo "OpenCV installation by learnOpenCV.com"

# --------------------------------------------------------
# Step 0: Select OpenCV version to install
sudo apt-get -y purge wolfram-engine
sudo apt-get -y purge libreoffice*
sudo apt-get -y clean
sudo apt-get -y autoremove

# this is where source will be cloned to
SOURCE_DIR=~/source/github.com/OpenCV
mkdir -p ${SOURCE_DIR}
cd ${SOURCEDIR}
# This is the stable version we will build
cvVersion="masrer"

INSTALL_DIR=/usr/local/lib
VENV_DIR="~/venv/OpenCV-${cvVersion}-py3"

# Clean build directories
if [ -d "opencv_${cvVersion}/build" ]; then
    rm -rf opencv_${cvVersion}/build
fi
if [ -d "opencv_contrib_${cvVersion}/build" ]; then
    rm -rf opencv_contrib_${cvVersion}/build
fi

# Create directory for installation
#mkdir installation
#mkdir installation/OpenCV-"$cvVersion"

# --------------------------------------------------------
# Step 1: Update Packages
sudo apt -y update
sudo apt -y upgrade

# --------------------------------------------------------
# Step 2: Install OS Dependencies & Libraries
sudo apt-get -y remove x264 libx264-dev

## Install dependencies
sudo apt-get -y install build-essential checkinstall cmake pkg-config yasm
sudo apt-get -y install git gfortran
sudo apt-get -y install libjpeg8-dev libjasper-dev libpng12-dev

sudo apt-get -y install libtiff5-dev
sudo apt-get -y install libtiff-dev

sudo apt-get -y install libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev
sudo apt-get -y install libxine2-dev libv4l-dev
cd /usr/include/linux
sudo ln -s -f ../libv4l1-videodev.h videodev.h
cd $cwd

sudo apt-get -y install libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
sudo apt-get -y install libgtk2.0-dev libtbb-dev qt5-default
sudo apt-get -y install libatlas-base-dev
sudo apt-get -y install libmp3lame-dev libtheora-dev
sudo apt-get -y install libvorbis-dev libxvidcore-dev libx264-dev
sudo apt-get -y install libopencore-amrnb-dev libopencore-amrwb-dev
sudo apt-get -y install libavresample-dev
sudo apt-get -y install x264 v4l-utils

# Optional dependencies
sudo apt-get -y install libprotobuf-dev protobuf-compiler
sudo apt-get -y install libgoogle-glog-dev libgflags-dev
sudo apt-get -y install libgphoto2-dev libeigen3-dev libhdf5-dev doxygen

# --------------------------------------------------------
# Step 3: Install Python Libraries
sudo apt-get -y install python3-dev python3-pip
sudo -H pip3 install -U pip numpy
sudo apt-get -y install python3-testresources

# We are also going to install virtualenv and virtualenvwrapper modules
# to create Python virtual environments.
cd $cwd
# Install virtual environment
python3 -m venv OpenCV-"$cvVersion"-py3
echo "# Virtual Environment Wrapper" >> ~/.bashrc
echo "alias workoncv-$cvVersion=\"source $cwd/OpenCV-$cvVersion-py3/bin/activate\"" >> ~/.bashrc
source "$cwd"/OpenCV-"$cvVersion"-py3/bin/activate
#############

# Next, we create the Python virtual environment.
############ For Python 3 ############
# now install python libraries within this virtual environment
sudo sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1024/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start
pip install numpy dlib
# quit virtual environment
deactivate

# --------------------------------------------------------
# Step 4: Download opencv and opencv_contrib
git clone https://github.com/opencv/opencv.git
cd opencv
git checkout $cvVersion
cd ..

git clone https://github.com/opencv/opencv_contrib.git
cd opencv_contrib
git checkout $cvVersion
cd ..

# --------------------------------------------------------
# Step 5: Compile and install OpenCV with contrib modules
# First we navigate to the build directory.

cd opencv
mkdir build
cd build

# Next, we start the compilation and installation process.

cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=${INSTALL_DIR}/OpenCV-"$cvVersion" \
      -D INSTALL_C_EXAMPLES=ON \
      -D INSTALL_PYTHON_EXAMPLES=ON \
      -D WITH_TBB=ON \
      -D WITH_V4L=ON \
      -D OPENCV_PYTHON3_INSTALL_PATH=${VENV_DIR}/lib/python3.5/site-packages \
      -D WITH_QT=ON \
      -D WITH_OPENGL=ON \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D BUILD_EXAMPLES=ON ..

make -j$(nproc)
make install

# --------------------------------------------------------
# Step 6: Reset swap file
# Once we are done with installing heavy Python modules like Numpy,
# it’s time to reset the swap file.

sudo sed -i 's/CONF_SWAPSIZE=1024/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start


# --------------------------------------------------------
# Finally, we also need to add a simple statement to 
# make sure that VideoCapture(0) works on our Raspberry Pi.

cp ~/.profile ~/.profile_$(date "%Y.%m.%d-%H.%M.%S")
cat ~/.profile | grep -v "sudo modprobe bcm2835-v4l2" > ~/.profile
echo "sudo modprobe bcm2835-v4l2" >> ~/.profile
