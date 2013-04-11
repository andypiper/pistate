#!/usr/bin/python

# import required libraries
import mosquitto
import RPi.GPIO as GPIO
import time
import socket
import os, sys

# function definitions
def on_connect(mosq, obj, rc):
    print("rc: "+str(rc))

def on_message(mosq, obj, msg):
    handle_msg(msg.topic, msg.payload)
    print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

def on_publish(mosq, obj, mid):
    print("mid: "+str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: "+str(mid)+" "+str(granted_qos))

def on_log(mosq, obj, level, string):
    print(string)

def getifip(ifn):
    import fcntl, struct
    sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(sck.fileno(),0x8915,struct.pack('256s', ifn[:15]))[20:24])

def getrevision():
  # Extract board revision from cpuinfo file
  myrevision = "0000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:8]=='Revision':
        length=len(line)
        myrevision = line[11:length-1]
    f.close()
  except:
    myrevision = "0000"

  return myrevision

def getserial():
  # Extract serial from cpuinfo file
  cpuserial = "0000000000000000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:6]=='Serial':
        length=len(line)
        cpuserial = line[11:length-1]
    f.close()
  except:
    cpuserial = "ERROR000000000"

  return cpuserial

def getgputemp():
  p = os.popen('/opt/vc/bin/vcgencmd measure_temp|cut -c6-9')
  gpu = p.readline()
  p.close

  return gpu

def getcputemp():
  z = os.popen('echo $((`cat /sys/class/thermal/thermal_zone0/temp|cut -c1-2`)).$((`cat /sys/class/thermal/thermal_zone0/temp|cut -c3-5`))')
  cpu = z.readline()
  z.close

  return cpu

def handle_msg(topic,data):
  # deduct one from the value of the LED number to find the index (starts at zero)
  led = int(topic[-1:])-1
  GPIO.output(LedSeq[led], True)


# main code starts here

# Tell GPIO library to use GPIO references
GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)

# List of LED GPIO numbers
LedSeq = [4,17,22,10,9,11]

# Set up the GPIO pins as outputs and set False
print "Setup LED pins as outputs"
for x in range(6):
    GPIO.setup(LedSeq[x], GPIO.OUT)
    GPIO.output(LedSeq[x], False)

# handle MQTT connection
mqttc = mosquitto.Mosquitto("pistate-" + str(os.getpid()))
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe
#mqttc.on_log = on_log

mqttc.connect("localhost", 1883, 60)

# fine to assign these to variables as they are
# unlikely to change during a session
pihost = socket.gethostname()
piipaddr = getifip("wlan0")
pirev = getrevision()
piserial = getserial()

mqttc.publish("pistate/host/name", pihost, 0, 1)
mqttc.publish("pistate/host/ip", piipaddr, 0, 1)
mqttc.publish("pistate/host/revision", pirev, 0, 1)
mqttc.publish("pistate/host/serial", piserial, 0, 1)

mqttc.publish("pistate/temp/cpu", getcputemp(), 0, 0)
mqttc.publish("pistate/temp/gpu", getgputemp(), 0, 0)

mqttc.subscribe("pistate/gpio/berryclip/led/#", 0)
mqttc.subscribe("pistate/gpio/berryclip/switch/#", 0)
mqttc.subscribe("pistate/gpio/berryclip/buzzer/#", 0)

rc = 0
while rc == 0:
  try:
    rc = mqttc.loop()

  except KeyboardInterrupt:
    print "Exiting"
    mqttc.disconnect()
    GPIO.cleanup()
    sys.exit(0)
