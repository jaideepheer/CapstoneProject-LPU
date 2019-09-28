# Setup environment
- First install Anaconda form [> this link <](https://www.anaconda.com/distribution/).

- Clone this reposatory to a folder on your computer.

- To setup codding environment run `start.bat`.

      The script automatically sets up python and tensorflow in an anaconda environment called `kapstone`.

- After executed once, run `start.bat` again to open the Jupyter lab. Make new notebooks and files there as required.

> Jupyter lab is currently not used in the project since I am creating the infrastructure for the application. I plan to use the lab to display processing progress and for GUI feedback like live display of video frames during processing or live display of audio transcript generated during processing.

##### In this stage, the project uses live_*_test.py files to test the code. Take a look at [`live_pipe_test.py`](./Code/live_pipe_test.py) for example.

If you want to develop, open the `Code` folder in your IDE as all files assume that `Code` is the root folder. This top level folder is only used to bundle `Code` and `deployment` folders.