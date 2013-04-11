PiState
=======

A Python-based MQTT publisher for data about the state of a Raspberry Pi and GPIO connected devices.

### Requirements

python-mosquitto MQTT client library
RPi.GPIO library for access to Raspberry Pi GPIO pins

### Current state

Currently works and publishes RPi host information along with onboard CPU and GPU temp.

Preliminary support for controlling BerryClip attached on the GPIO pins.

### TODO

 * error handling around CPU/GPU etc
 * looping temperature update
 * check for root access
 * exit handler
 * daemonize
 * config files