
'''
IMPORTANT MUST READ

It is necesary to activate SPI in Raspberry configuration (for the screen to work)

Some neccesary apt installs (sudo apt install "name") in the terminal before
compiling a version of python 3.11:
"sudo apt-get install portaudio19-dev" for sounddevice numpy to work
sudo apt install libasound2-dev  # Sound and/or recording
sudo apt install libpulse-dev	# Sound and/or recording
sudo apt install libsndfile-dev libsamplerate0-dev	# Sound and/or recording

sudo apt install libssl-dev		#SSL

sudo apt-get install aptitude	#before installing pillow, install aptitude for dependencies
sudo aptitude install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk libharfbuzz-dev libfribidi-dev libxcb1-dev
sudo apt-get install meson	#libraqm, that allows to have wheels

sudo apt-get install python3-pil python3-pil.imagetk #PIL or Pillow

sudo apt install python3-tk 	#TKinter
sudo apt-get install tk-dev		#TKinter
sudo apt-get install python-tk python3-tk tk-dev	#TKinter

sudo aptitude install portaudio19-dev	#pyaudio


sudo apt-get install libatlas-base-dev python3-dev python3-pip # Pandas dependencies
sudo aptitude install python3-pandas	#Pandas
python3.11 -m pip install --upgrade pandas
python3.11 -m pip install --upgrade more_itertools



PILLOW have issues installing.
Try - only after installing all pillow dependencies (including Wheels):
python3.11 -m pip install --upgrade Pillow --no-binary :all:


'''

import importlib
import subprocess
import os

song_name = 'jingle_bells easy'

# Update the working directory
new_directory = r"/home/cristobal/music_assistant"
os.chdir(new_directory)

# Now the working directory has been changed
print("Working directory changed to:", os.getcwd())

required_libraries = [
    "numpy",
    "Pillow",
    "image",
    "blosc2",
    "cython",
    "tables",
    "pretty_midi",
    "pyaudio",
    "aubio",
    "pandas",
    "more-itertools",
    "pygame",
    "adafruit-circuitpython-lis3dh",
    "adafruit-circuitpython-rgb-display",
    "adafruit-blinka",
    "adafruit-blinka-pyportal",
    "adafruit-circuitpython-hx8357",
    "sounddevice numpy",
    "adafruit-circuitpython-touchscreen",
    "libasound2-dev",
    "libpulse-dev",
    
    
]

def install_libraries(libraries):
    for library in libraries:
        try:
            importlib.import_module(library)
            print(f"{library} is already installed.")
        except ImportError:
            print(f"Installing {library}...")
            subprocess.run(["python3.11", "-m", "pip", "install", library])
            print(f"{library} installed successfully.")


import os

# List of directories to create
directories = [
    "MIDI Files",
    "MIDI_to_CSV_songs",
    "player_recorded_tunes",
    "Screens",
    "Screens/Introduction_sequence",
    "Screens/Player_reports"

]

def create_directories(directories):
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
        else:
            print(f"Directory already exists: {directory}")


            
if __name__ == "__main__":
    install_libraries(required_libraries)
    create_directories(directories)
    
