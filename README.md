# ido booth #

This is the software I wrote for the photo booth at our wedding. It consists of a simple Python script for the Raspberry Pi with camera and buttons.

## Functionality ##

The enclosed booth was set up in the back of the room. One button takes three shots, while the other records a slow motion video. The main screen loops through the photos that were taken.

There was no printer, as I considered anything mechanical a risk for something nearly untested. All pictures and videos were just stored on the SD card. After the party, I made a video montage from the slowmotion videos and put it together with all photos on a 'thank you' web page. We also distributed personal photo strips and put the pictures as miniatures in our wedding album. The cheapest option for the strips is to assemble two strips on a standard postcard format photo with mogrify, print them and cut them by hand.

You could do the same with better photo results (and a flash) using a DSLR controlled with gPhoto2, although you would probably lose the slow motion videos. Mine was not supported and buying a new one would for this would be way more expensive than just renting a photo booth.

## Hardware ##

Requirements:
* Raspberry Pi 3B
* Raspberry Pi power adapter
* Pi Camera Module v2
* Micro SD-card with some room for photos
* Jumpers and cables
* Bedside table
* Two push buttons
* LCD display
* Display mount kit

I drilled two holes in the top of my bedside table and put industrial push buttons in them that my dad had lying around. I did not use a breadboard but directly connected them to the GPIO pins of a Raspberry Pi 3B on the inside using old motherboard jumper cables. A Raspberry Pi Camera hung in front of another hole in the back near the top. One last hole in the back led a HDMI and power cable to a computer monitor that was mounted on the back. At the party, we simply put it on a reception table.

From a frame for an old pool tent and black fleeces my parents had lying around, we made a large square frame for the booth. In the back we hung helium balloons for decoration.

The only thing we had to buy for this whole setup was the Raspberry Pi, its power supply and camera, so the cost was little to nothing.

Unfortunately, I did not make pictures and in the mean time gave the bedside table away. Yes, someone was actually interested in a bedside table with four holes drilled into it.

## Software ##

Because of the excellent pygame, RPi and picamera libraries, all pieces of the puzzle were there and I just had to glue them in place. I was inspired by similar scripts, notably [boothy](https://github.com/zoroloco/boothy), [pi-photo-booth](https://github.com/jcroucher/pi-photo-booth), [raspberry-pi-photo-booth](https://github.com/easy-rider4/raspberry-pi-photo-booth) (thank you!).

The interface was modelled after the invitation website that I put up, using the Economica font and black and white icons in circles. Since the physical buttons were not labeled, there were on-screen indicators for them in the top edge corners of the main screen.

There is a simple systemd script to keep it running and restart if it crashed (luckily that did not happen).

## License ##

Feel free to find inspiration, copy and distribute. Because of its simplicity
it is almost ridiculous to put it under any kind of license, but if you insist:

    Copyright (C) 2019  Raf Pauwels

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
