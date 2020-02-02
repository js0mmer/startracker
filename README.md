# startracker
Code for a barn door star tracker enabling you to take longer exposures of the night sky and capture deep sky objects with a DSLR.
Runs on a Raspberry Pi connected to a WiFi network, controlled from the [Blynk](https://blynk.io/) app.

![My sketch](https://i.imgur.com/ZJV0bvF.png)
![Blynk](https://i.imgur.com/fbsSxXQ.jpg)

![My build](https://i.imgur.com/hatQ5ix.jpg)
![The Orion Nebula](https://i.imgur.com/2u5nA0O.png)

Parts:
- Hinge 3 1/2" wide
- 3 Aluminum Tubes 1/8"x12"
- Pine Board 1x4"x4'
- 3/8" Washers
- 2 1/4" T-nuts
- 2 1/8" Washers
- Threaded Rod 1/4"x12"
- Acorn Nut 1/4"
- [5mm coupling shaft](https://www.amazon.com/gp/product/B01HBV4KCE)
- 3/8" bolt
- [28BYJ-48 Stepper motor](https://www.amazon.com/ELEGOO-28BYJ-48-ULN2003-Stepper-Arduino/dp/B01CP18J4A)
- [Pergear TH3 ball head mount](https://www.amazon.com/TH3-Capacity-U-Shaped-Switching-Vertical/dp/B00MGJH5U6)
- Raspberry Pi (any will work)
- USB Battery Bank
- Epoxy

Based off of [this design](https://partofthething.com/thoughts/making-a-cheap-and-simple-barn-door-star-tracker-with-software-tangent-correction-for-astrophotography/).

## How it works
In order to track stars and deep sky objects as they rotate through the sky, the camera needs to follow them. This is done by mounting it on a star tracker which as pointed at one of the celestial poles (in my case the North Pole as I am in the Northern Hemisphere). There are many devices out there that do this but they are all very expensive so I decided to build my own. My contraption is composed of two wooden boards connected by a hinge with the DSLR mounted on top via a ball head mount. The first key component of using the star tracker is that the hinge has to be pointed directly at the North Celestial Pole when in use. Second, in order for the star tracker to work properly, it needs to rotate at the same angular velocity that the Earth rotates at but in the opposite direction. A day is 24 hours long so that angular velocity would be about 1 rotation per 24 hours, right? Initially, I started off with that value but later switched to the more accurate angular velocity of 1 rotation per 1 sidereal day. You can read up more on [sidereal time here](https://en.wikipedia.org/wiki/Sidereal_time) but basically it is Earth's rotation rate relative to the fixed stars and is used by astronomers. To achieve this angular velocity, the top wooden board is pushed upward by a threaded rod that is being driven by a stepper motor as seen in the picture above. The motor slides up the aluminum rods as the threaded rod is screwed into the t-nut. The Raspberry Pi actively calculates how much to step the motor based on the number of steps for each rotation, the threads per inch of the rod, and the distance it needs to travel upwards every second to maintain the angular velocity of 1 rotation/sidereal day. The math gets slightly complicated, but to sum it up the distance is calculated using trigonometric functions since the wooden boards and the threaded rod form a right triangle. The length of the bottom board is known and the initial distance the threaded rod sticks up is known so they can be used to calculate the angle the top board makes with the bottom one. Every second, the program calculates the new angle the star tracker should be at using the angular velocity. From this, the program uses the inverse tangent function to calculate the distance the threaded rod needs to travel since it knows the angle and the length of the base. It then aggregates this value to the height variable in order to keep track of it so the correct calculation can be made the next time it loops, a second later. My star tracker is controlled through Blynk which is an open Internet of Things platform that alllows me to create a project within their smartphone app that will communicate with my python program to start and stop tracking. The image of space you see above is of the Orion Nebula and was taken with this Star Tracker by taking 150 5-second exposures  at a 300mm focal length and stacking them. Without the star tracker, I could have only gone up to a 1.3 second exposure at 300mm which is not sufficient enough to capture dim deep sky objects. This device effectively allows me to take exposures that are about 4 times longer which makes a big difference, especially when using lower focal lengths and being able to lengthen the exposure time. It could allow up to 2 minute exposures at 18mm as compared to 30 seconds without it.