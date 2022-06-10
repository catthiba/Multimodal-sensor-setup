# Multimodal-sensor-setup
The repository include custom code enabling proprietary hardware to utilize the open source software distribution LSL. The custom scripts implemented for the Shimmer sensors are inspired from the examples provided by ShimmerReserch's GitHub repository for Shimmer3 units. The scripts can be found [here](https://github.com/ShimmerResearch/shimmer3/tree/master/LogAndStream/python_scripts).


## Table of content
- [Repository Structure](#repository-structure)
  - [sensors](#sensors)
  - [xdf](#xdf)
- [Installation](#installation)
  - [Clone Repository](#clone-repository)
  - [Conda](#conda)
  - [PIP](#pip)
  - [LabRecorder](#labrecorder)
- [Usage](#usage)
  - [Linux](#linux)
  - [Windows](#windows)
  - [Run Experiment](#run-experiment)

## Repository Structure
### Sensors 
This folder contains the files needed to conduct the experiment. The scripts include ShimmerCommands.py, ECG_to_LSL.py and GSR_to_LSL.py, and EEG_to_LSL. The scripts are gathered in the main.py file, which is the one sending all stremas to LSL.
### xdf
This folder contains scripts where xdf files are converted to csv, plotted or simply opening the content of the file.


## Installation
In order to run this repository, and use LSL follow these steps. The setup is tested on both linux and windows operative system.

It is good practice to use virtual environments, in order to have control of the installed packages and libraries. You can eighter use Anaconda and the conda environment, or install virtualenvironment. Both guides are given below, one only need to follow the instructions for Conda or PIP.

### Clone Repository 
In terminal of preference, go to directory you want the repository to be added. To clone the repository run the command:
```
git clone https://github.com/catthiba/project-thesis.git
```
Direct into the folder project-thesis, and then to the folder src. 

### Conda

If you dont have Anaconda already installed, you can follow [the Windows guide](https://www.datacamp.com/community/tutorials/installing-anaconda-windows) for installation. Or if you have linux you can follw [the Linux guide](https://www.datacamp.com/community/tutorials/installing-anaconda-windows). Open your terminal or Anaconda prompt and follow the steps:

Create and activate Anaconda environment, your_environment should be replaced by desired name for the environment:

```
conda create --name your_environment
```
Type y when conda asks you to proceed

Windows activation:

```
conda activate your_environment
```

Linux activation:

```
source conda activate your_environment
```
#### Required libraries

Install LSL:

```
conda install -c tstenner pylsl
```
and,

```
conda install -c conda-forge liblsl
```

Install Serial Port:

```
conda install pyserial
```

### PIP

If you dont have PyPI already installed, you can follow [the Windows guide](https://phoenixnap.com/kb/install-pip-windows) for installation. Or if you have linux, follow [the Linux guide](https://www.geeksforgeeks.org/how-to-install-pip-in-linux/).

Create and activate virtual environment with virtualenv package

```
pip install virtualenv  && virtualenv your_environment
```

Windows activation:

```
your_environment\Scripts\activate
```

Linux activation:

```
source your_environment/bin/activate
```
#### Required libraries

Install LSL

```
pip install pylsl
```

Install Serial Port

```
pip install pyserial
```

### LabRecorder

The program can be downloaded through LSL's own [GitHub repository](https://github.com/labstreaminglayer/App-LabRecorder/releases). The program is cross-platform, supported by the popular operative system such as Windows, OSX, Android, and Linux. The dependencies of the program must be downloaded and installed if the program is running on Linux Ubuntu. 

## Usage

LabRecorder has a user-friendly interface, making it easy to start the recording session. The interface consists of three sections. A Recording control section where the user can start and stop the recording. A Record from Streams section where all available device streams are displayed, and lastly a Saving to section, where the location of the file is displayed, in addition to configuration settings of the file. 

If only specific streams are wanted they can be selected as needed. LabRecorder must be updated if a device is turned on after initiating the program. When the setup is ready, the user can start recording the measurements.

First you have to connect to the Shimmer sensor units. This is done differently on Windows and Linux.

### Linux

To run the scripts and connect to the sensor units, you need admin priveleges.

First you need to find the MAC-address, by running:

```
hcitool scan
```

The output will look something like this:

```
00:06:66:D7:C6:F2	Shimmer3-C6F2
```

Check that there are no other serial connections running.

```
sudo killall rfcomm
```

Connect to the Shimmer with:

```
sudo rfcomm connect /dev/rfcomm0 <MAC-adress> 1 &
```

When connecting to the sensors for the first time a window will pop up on the screen and ask you to type in a pin code. This pin code is:

```
1234
```

### Windows

Connect to the Shimmer sensor units through the Bluetooth UI that can be found either by clicking on the Blutetooth symbol in the windows task bar and click on open settings, or by searching for Bluetooth settings in the search field. Click on "Add Bluetooth or other device", then on "Bluetooth". Find the shimmer device you want to connect and doubble click on it. On the back of the Shimmer3 device it has an id, the name of the device will be "Shimmer3-id". It will ask you for a pin, type in the pin "1234", click "connect" => "done".

To check which comport it is using the device is using, click on "More Bluetooth options" => "Com Ports". Here you will see overview of COM ports, the direction and name of device. 

If the device do not have an outgoing COM port already you have to add on by clicking "Add...", check of for outgoing, find the device in the dropdown list and click "Ok". 

Note which outgoing COM port the device have, because when you are running the scripts you need to know which comport to use.

### Run Experiment

1. Open LabRecorder.
2. To conduct the experiment with the Shimmer sensors and LabRecorder you have to run the scripts ECG_to_LSL.py and GSR_to_LSL.py in seperate terminals/command prompts and the environment created earlier have to be activated. Ensure that you are in the right working directory, the src folder. 

    Linux:

      ```
      sudo python3 ECG_to_LSL.py /dev/rfcomm0
      ```
      
      ```
      sudo python3 GSR_to_LSL.py /dev/rfcomm0
      ```
    Windows, use the corresponding outgoing COM ports to the devices:

      ```
      python ECG_to_LSL.py <COMPORT>
      ```

      ```
      python GSR_to_LSL.py <COMPORT>
      ```

<!-- ... RunExperiment.py. The sensors are now available to the LSL network.
   Linux:

   ```
   sudo python3 RunExperiment.py /dev/rfcomm0
   ```

   Windows:

   ```
   python RunExperiment.py <COMPORT>
   ```-->

3. Update LabRecorder and select the sensors you want.
4. Start experiment. Both the scripts for the ECG and GSR device, and LabRecorder must run simultaniously in order to collect data.
5. Stop experiment. The data will be saved to an xdf file.
6. View the data by running xdf.py, before running the script, it have to be modifed to have the correct file path. Open the script and change the line bellow with to the path where the file is saved.

    ```
    data, header = pyxdf.load_xdf('file_path')
    ```
7. The additional dependencies have to be installed: 

    Install Pyxdf

      ```
      conda install -c conda-forge oyxdf
      ```

        or:

      ```
      pip install pyxdf
      ```

    Install matplotlib

      ```
      conda install matplotlib
      ```

        or:

      ```
      pip install -U matplotlib
      ```
9. Run the xdf.py file:
    Linux:

      ```
      sudo python3 xdf.py
      ```

    Windows:

      ```
      python xdf.py
      ```
