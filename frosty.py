#First we need to import the LED & Pause class from the GPIO Zero Library

from gpiozero import LED

#We also need the sleep function from the time library

from time import sleep

#Along with pause which we will use later on

from signal import pause


#Next we need to create a nose object and assign it a class of an LED.

#This gives us all of the functions available for the LED module in GPIO Zero.

 

nose = LED(25)
whites = [ 
    LED(9),   #1
    LED(8),   #2
    LED(7),   #3 
    LED(17),  #4
    LED(18),  #5
    LED(22),  #6
    LED(23),  #left 
    LED(24)   #right
    #LED(14), 
    #LED(11), 
    #LED(3), 
    #LED(10), 
    #LED(15), 
    #LED(27), 
    #LED(4), 
    #LED(2) 
    ]

while True:
    for led in whites:
        led.on()
        sleep(.5)

    #Now we're setup we can go through some of the available commands! 
    #Let's begin by turning the nose on!

    nose.on()

    #And wait 1 second

    sleep(1)

    #And now turn the nose off,

    nose.off()

    sleep(1)


    #We can also toggle the LED instead. 
    #This means if the LED is already on it will
    #turn it off and if it's off turn it on.
    #Lets try that now with a sleep inbetween

    nose.toggle()
    sleep(1)

    nose.toggle()
    sleep(1)

    #Quite simple, we could put this into a while True: loop and have it blink forever
    #However GPIO Zero has a neat little blink function.

    nose.blink()

    sleep(15)

    for led in reversed(whites):
        led.off()
        sleep(.5)
   
#And finally if you've got all of your LEDs blinking you can then use
#the pause function to make it run until quit using Ctrl-C
#pause()


#And that's the end of this basic tutorial on blinking an LED on the SnowPi!

#The rest is up to you to decide on patterns you wish to make.
