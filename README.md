The purpose of this program is to fetch and display the departure times of the nearest metro-station in my hometown of Stockholm.
It is done by an interval-loop that every 10 seconds fetches the current display-time from an endpoint found in the SL-web API. 
After the information is fetched in the loop, the relevant departures are then extracted and sent to the LED-matrix panel.

The hardware being used for this is:
1. A Raspberry pi Pico W
2. A Waveshare LED-matrix panel

The microcontroller is programmed and booted in Micropython and the IDE used for this project was Mu-editor.
