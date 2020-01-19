
Tutorial
========

The basic user interface is simple and intuitive and is based on drag'n'dropping the cameras into views.

1. Manage Cameras
-----------------

First, let's register some RTSP cameras.

- Navigate to *Configuration / Configuration Dialog / Camera Configuration*
- Choose a slot for the camera
- Choose *RTSP Camera* from the drop-down menu
- Type in the camera information (ip address, user, password, etc.)
- Repeat for all cameras
- Press *SAVE*
- Close the window from the upper-right (X) as usual

You should also give an estimate of the number of hd-ready, full-hd, 2K etc. streams in *Memory Configuration* tab, as Valkka pre-reserves all resources


2. Viewing Cameras
------------------

Let's see a list of installed cameras and view their live video

- Navigate to *View / Camera List*.  The camera list widget appears on screen
- Navigate to *View / Video Grid / 2x2*.  A 2x2 grid appears on the screen
- Drag and drop cameras from the camera list widget into the 2x2 grid
- You can open as many video grids on the screen as you please
- Note that even if you view the same video in multiple grids, the camera stream is decoded only once
- Note that you can also do drag and drop between video grids
- Double-clicking on the video, maximizes the video size
- Double-clicking again, restores the normal size

3. Removing Cameras
-------------------

- Right-click on a video in the video grid
- Choose *Remove Camera*

4. Saving and Loading the Layout
--------------------------------

Camera views can be saved, and recovered for the next time when you use Valkka Live

- Navigate to *File / Save Window Layout*.  Now your view layout is saved
- When starting the program again, navigate to *File / Load Window Layout*

5. Machine Vision
-----------------

- Open a machine vision terminal from the *Machine Vision* menu
- Drag'n drop a camera to that terminal

