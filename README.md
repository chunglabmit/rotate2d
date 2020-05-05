# rotate2d - a GUI for rigid rotation

To install:

* Create and activate a virtual environment, e.g.
  ```bash
  conda create -n rotate2d python pip
  conda activate rotate2d
  ```

* Clone rotate2d and PIP install it, e.g.
    ```bash
    git clone https://github.com/chunglabmit/rotate2d
    pip install ./rotate2d  
  ```

To run:
  ```bash
  rotate2d
  ```

To use:

From the menu, select File -> Open Fixed and pick a ZARR directory,
select File -> Open Moving and pick a ZARR directory. Hit the button
marked "Center" to set the center for rotation, then hit the button
marked "Show" to show the fixed image in red and the moving image in
green.

You may have to select the z slice for each using the z-height controls
and for large images, set "Downsample" to 2 or more to reduce the
display image size. After any change, hit "Show" to redisplay.

You should adjust the offsets and angle until the images align. Then
select File -> Save from the menu. This will let you save the rotation
and translation parameters as a JSON file. 