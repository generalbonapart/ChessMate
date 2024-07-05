sudo apt-get update
sudo apt-get install build-essential cmake pkg-config libjpeg-dev libtiff5-dev libjasper-dev libpng-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libfontconfig1-dev libcairo2-dev libgdk-pixbuf2.0-dev libpango1.0-dev libgtk2.0-dev libgtk-3-dev libatlas-base-dev gfortran libhdf5-dev libhdf5-serial-dev libhdf5-103 python3-pyqt5 python3-dev -y

sudo apt install git -y
git clone https://github.com/generalbonapart/ChessMate.git

sudo apt install python3-dev
sudo apt install libgl1-mesa-glx
sudo apt install i2c-tools -y

pip install -r chessApp/requirements.txt