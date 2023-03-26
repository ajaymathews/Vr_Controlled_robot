sleep 30
sudo uv4l --driver raspicam --auto-video_nr --server-option '--port=5000' --encoding mjpeg --server-option '--enable-webrtc' --width 256 --height 288 --framerate 24 --vflip --hflip

sudo kill `sudo lsof -t -i:8080`
sleep 1
cd /home/pi/Downloads/cardboardstream/server

sudo python server.py

#sleep 2 

#cd /home/pi/Downloads/cardboardstream/server

#sudo python Control.py
