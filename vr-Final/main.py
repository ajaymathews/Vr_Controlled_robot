from flask import Flask
from Adafruit_PWM_Servo_Driver import PWM
import math
import subprocess
import RPi.GPIO as g
import time
import serial
import thread
import thingspeak

channel_id = '315007'
write_key  = 'O6GYF8LJOKAX8N6Z'

channel = thingspeak.Channel(id=channel_id,write_key=write_key)

app = Flask(__name__)

pwm = PWM(0x40)

arm=serial.Serial('/dev/ttyUSB0',9600,timeout=.1)

# Constants defining the range of the servo
SERVO_MIN = 150
SERVO_MAX = 600
HALF_PI = math.pi / 2.0
MIDPOINT = 375.0
SPAN = 225.0

MIDPOINT1 = 150.0
SPAN1 = 225.0

# channels
PAN = 1
TILT = 0
b=2
fb=3
ud=4
p=5


g.setmode(g.BOARD)
g.setwarnings(False)
g.setup(37,0)
g.setup(35,0)
g.setup(33,0)
g.setup(31,0)

g.setup(40,1,pull_up_down=g.PUD_UP)
g.setup(38,1,pull_up_down=g.PUD_DOWN)
g.setup(36,1,pull_up_down=g.PUD_DOWN)

g.output(37,0)
g.output(35,0)
g.output(33,0)
g.output(31,0)


def fwd():
    g.output(37,1)
    g.output(35,0)
    g.output(33,1)
    g.output(31,0)

def stop():
    g.output(37,0)
    g.output(35,0)
    g.output(33,0)
    g.output(31,0)

def rev():
    g.output(37,0)
    g.output(35,1)
    g.output(33,0)
    g.output(31,1)

def left():
    g.output(37,1)
    g.output(35,0)
    g.output(33,0)
    g.output(31,1)

def right():
    g.output(37,0)
    g.output(35,1)
    g.output(33,1)
    g.output(31,0)




def init():
    pwm.setPWMFreq(60)
    pwm.setPWM(PAN, 0, 375)
    pwm.setPWM(TILT, 0, 375)
    pwm.setPWM(b, 0, 375)
    pwm.setPWM(fb, 0, 375)
    pwm.setPWM(ud, 0, 375)
    pwm.setPWM(p, 0, 375)



met=0
pir=0
gas=0
def status():
    global met,pir,gas
    while 1:
        if(g.input(40)==0):
            print 'gas detected'
            gas=1
        else:
            gas=0
        if(g.input(38)==1):
            print 'pir dete'
            pir=1
        else:
            pir=0
        if(g.input(36)==1):
            print 'metal'
            met=1
        else:
            met=0
        try:
            response = channel.update({1:str(gas)+','+str(pir)+','+str(met)})
            print response
        except:
            print "connection failed"
       


arm_ud=375
arm_fb=375
arm_b=375
arm_flag=0
arm_p=375
def cntl():
    global arm_ud,arm_fb,arm_b,arm_p,arm_flag
    while(1):
        a=arm.readline()
        #print a
        if 'f' in a:
            print 'fwd'
            fwd()
        if 'b' in a:
            print 'bck'
            rev()
        if 'l' in a:
            print 'left'
            left()
        if 'r' in a:
            print 'right'
            right()
        if 's' in a:
            print 'stop'
            stop()
        if 'a' in a:
            print 'pick'
            arm_flag=arm_flag+1
            print arm_flag
            if arm_flag==1:
                arm_p=375
            if arm_flag==2:
                arm_p=550
                arm_flag=0
        if '#' in a:
            if '*' in a:
                data=a[a.index('#')+1:a.index('*')]
                print data
                data=data.split(',')
                arm_ud=int(data[0])
                arm_fb=int(data[1])
                arm_b=int(data[2])
        
        pwm.setPWM(b, 0, arm_b)
        pwm.setPWM(fb, 0, arm_fb)
        pwm.setPWM(ud, 0, arm_ud)
        pwm.setPWM(p, 0, arm_p)
        




@app.route('/')
def hello():
    return "hello"


def normalize(num):
    '''
    num: a float between -PI and PI.
    returns: num normalized between SERVO_MIN and SERVO_MAX.
    '''
    return int(MIDPOINT + ((num / HALF_PI) * SPAN))
def normalize1(num1):
    '''
    num: a float between -PI and PI.
    returns: num normalized between SERVO_MIN and SERVO_MAX.
    '''
    return int(MIDPOINT1 + ((num1 / HALF_PI) * SPAN1))


@app.route("/move/<pitch>/<yaw>")
def move(pitch, yaw):
    pwm.setPWM(TILT, 0, normalize1(-float(pitch)))
    pwm.setPWM(PAN, 0, normalize(float(yaw)))
    return "OK"




try:
    init()
    thread.start_new_thread(status,() )
    thread.start_new_thread(cntl,() )
    app.run(host='192.168.43.135', port=8080, debug=True, use_reloader=False)


except:
    print 'err'
    pass


while 1:
   pass

