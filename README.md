# Robot-power-module GUI V1
Henk Kiela Probotcs BV, Opteq Mechatronics BV

Titel: Python 3x version of GUI for Robot Power Module

This is the new Python 3 based GUI for the Robot Power module of Probotics BV allowing cross OS usability

Look at:
http://probotics.eu/om2082-robot-power-manager-met-2-batterijen-en-6-geschakelde-uitgangen

Suppose you have a mobile robot with drives, wheels, various on board controllers and (environmental) sensors,
you definitely want to be able to monitor battery condition, control power to various modules only when needed, etc.

This Robot Power Module allows you to do so.
The Python GUI gives you a simple interface to operate the Power Module in an intuitive way.

This is a first version. There are still a lot of things on the to-do list like:
- socket interface to allow remote operating systems and for example ROS to hook on in a simple and efefctive manner
- better looking gui interface
- Local light weight serialport<-> socket interface and GUI with socket interface to allow multiple GUI's to connect to one 
  power module simultanouisly.
  
  
  
