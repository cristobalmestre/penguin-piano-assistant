import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import subprocess
from multiprocessing import Process, Queue
import Comparison_scoring  # Import the subprocess that will give variables back to the code
import os
import digitalio
import board
from adafruit_rgb_display import hx8357


# from adafruit_hx8357 import HX8357 as touchscreen

# import adafruit_touchscreen

# Update the working directory
from config_assistant import new_directory
os.chdir(new_directory)


class App:
    def __init__(self, root):
        self.root = root
        self.stage = 0
        self.image_folder = os.path.join("Screens", "Introduction_sequence")
        self.images_intro = ["1 Music Sheet.png", "2 Music Sheet after.png", "3 Recording Start.png", "4 Recording During.png", "5 Recording Finished.png"]
        self.image_results_folder = os.path.join("Screens", "Player_reports")
        self.images_result = ["1.png", "2.png", "3.png", "4.png","5.png","6.png","7.png","8.png","9.png"]

        self.result_queue = Queue()  # Create a multiprocessing Queue for communication

        
        self.label = tk.Label(root)
        self.label.pack()
        
        
        # Code for configurating the display
        
        # Configuration for CS and DC pins (these are PiTFT defaults):
        self.cs_pin = digitalio.DigitalInOut(board.CE0)
        self.dc_pin = digitalio.DigitalInOut(board.D25)
        self.reset_pin = digitalio.DigitalInOut(board.D24)

        # Config for display baudrate (default max is 24mhz):
        self.BAUDRATE = 24000000

        # Setup SPI bus using hardware SPI:
        self.spi = board.SPI()
        
        # Create the display:

        self.disp = hx8357.HX8357(self.spi, rotation=270,                           # 3.5" HX8357
            cs=self.cs_pin,
            dc=self.dc_pin,
            rst=self.reset_pin,
            baudrate=self.BAUDRATE,
        )
        
                
        # End of code for configurating the display

                
        '''
        self.touchscreen = adafruit_touchscreen.Touchscreen(
            digitalio.DigitalInOut(board.TOUCH_X),
            digitalio.DigitalInOut(board.TOUCH_Y),
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT,
        )
        

        # the "self.label.bind("<Button-1>", self.next_stage)"  line is replaced by the following, so the touchscreen allows the tapping
        self.touchscreen.on_press = self.next_stage
        '''
        #self.label.bind("<Button-1>", self.next_stage)  # Bind left mouse click event
        self.button = tk.Button(root, text="next", command=self.next_stage)
        self.button.pack()

        # Load the first image
        self.next_stage()


    def next_stage(self, event=None):
        if self.stage < len(self.images_intro):
        # the previous line is replaced by the following, so the touchscreen allows the tapping
#         if self.stage < len(self.images_intro) and self.touchscreen.touch_point:
            print("Executing next_stage for", self.stage)
            image_path = os.path.join(self.image_folder, self.images_intro[self.stage])
            
            self.show_image(image_path)
            
            '''
            # Old coding to display the image
            image = Image.open(image_path)
            # Display image.
            disp.image(image)
            # self.display_image(image_path)

            '''


            if self.stage == 3:  # Stage where the recording starts
                self.stage += 1  # Advance to the next stage
                self.root.after(1000, self.execute_Read_MIDI_record)  # Schedule the code for the fourth image after a delay
                
            elif self.stage == 4: # Stage where the recording stops and get saved
                self.remove_flag_file()
                self.stage += 1  # Advance to the next stage
           
            else:
                self.stage += 1  # Advance to the next stage

        else: # Stage that does the comparison and produce the results
            self.execute_compare()
            self.stage =1


    def display_image(self, image_path):

        #self.terminate_subprocess()  # Terminate the subprocess if it's running
    
        img = Image.open(image_path)
        img = img.resize((SCREEN_WIDTH, SCREEN_HEIGHT), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        self.label.config(image=img)
        self.label.image = img

 
    # This code will Read the MIDI File, transform it, then listen to the recording and stop it over the next click
    def execute_Read_MIDI_record(self):
        flag_file = "stop_processing.flag"
        if os.path.exists(flag_file):
            os.remove(flag_file)  # Remove the flag file if it exists

        # Start the subprocess and store the subprocess object
        # Read_MIDI_record_compare.py is the code that does the recording
        print("Executing code for stage", self.stage)
        self.subprocess_Read_MIDI = subprocess.Popen(["python", "Read_MIDI_record_compare.py"])

        # Schedule a method to check the subprocess status after a certain time
        self.root.after(1000, self.check_subprocess_status)


    # Helper function to finish recording after tapping the screen N1
    def check_subprocess_status(self):
        # Check if the subprocess is still running
        if self.subprocess_Read_MIDI.poll() is None:
            # The subprocess is still running, schedule the check again after a delay
            self.root.after(1000, self.check_subprocess_status)
        else:
            # The subprocess has finished, clean up
            self.remove_flag_file()
    
    # Helper function to finish recording after tapping the screen N2
    def remove_flag_file(self):
        flag_file = "stop_processing.flag"
        if os.path.exists(flag_file):
            os.remove(flag_file)

    # Function that compares the played and original song. It calls Comparison_scoring.py 
    def execute_compare(self):
    
        # Test to locate the pointer
        print("Executing code for stage", self.stage)
        print("We will compare and display the result here")

        # This line calls the Comparison_scoring.py file, which does the comparison
        abs_pitch_score, pitch_category, time_score, time_category = Comparison_scoring.calculate_scores()

        print("results recieved")

        #print(f"Pitch Score: {abs_pitch_score:.0f}, Pitch Category: {pitch_category}")
        #print(f"Time Score: {time_score:.0f}, Time Category: {time_category}")
        print("Pitch Score: {:.0f}, Pitch Category: {}".format(abs_pitch_score, pitch_category))
        print("Time Score: {:.0f}, Time Category: {}".format(time_score, time_category))



        if pitch_category == "high":

            if time_category == "high":
                print("Screen 9")
                image_path = os.path.join(self.image_results_folder, self.images_result[8])
                self.show_image(image_path)

            elif time_category == "medium":
                print("Screen 6")
                image_path = os.path.join(self.image_results_folder, self.images_result[5])
                self.show_image(image_path)

            else:
                print("Screen 3")
                image_path = os.path.join(self.image_results_folder, self.images_result[2])
                self.show_image(image_path)

        elif pitch_category == "medium":

            if time_category == "high":
                print("Screen 8")
                image_path = os.path.join(self.image_results_folder, self.images_result[7])
                self.show_image(image_path)

            elif time_category == "medium":
                print("Screen 5")
                image_path = os.path.join(self.image_results_folder, self.images_result[4])
                self.show_image(image_path)

            else:
                print("Screen 2")
                image_path = os.path.join(self.image_results_folder, self.images_result[1])
                self.show_image(image_path)


        else:

            if time_category == "high":
                print("Screen 7")
                image_path = os.path.join(self.image_results_folder, self.images_result[6])
                self.show_image(image_path)

            elif time_category == "medium":
                print("Screen 4")
                image_path = os.path.join(self.image_results_folder, self.images_result[3])
                self.show_image(image_path)

            else:
                print("Screen 1")
                image_path = os.path.join(self.image_results_folder, self.images_result[0])
                self.show_image(image_path)
                
                
    def show_image(self, image_path):

        # pylint: enable=line-too-long

        # Create blank image for drawing.
        # Make sure to create image with mode 'RGB' for full color.

        if self.disp.rotation % 180 == 90:
            height = self.disp.width  # we swap height/width to rotate it to landscape!
            width = self.disp.height
        else:
            width = self.disp.width  # we swap height/width to rotate it to landscape!
            height = self.disp.height


        image = Image.new("RGB", (width, height))

        # Get drawing object to draw on image.
        draw = ImageDraw.Draw(image)

        # Draw a black filled box to clear the image.
        draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
        self.disp.image(image)


        image = Image.open(image_path)


        # Scale the image to the smaller screen dimension
        image_ratio = image.width / image.height
        screen_ratio = width / height
        if screen_ratio < image_ratio:
            scaled_width = image.width * height // image.height
            scaled_height = height
        else:
            scaled_width = width
            scaled_height = image.height * width // image.width
        image = image.resize((scaled_width, scaled_height), Image.BICUBIC)



        # Crop and center the image
        x = scaled_width // 2 - width // 2
        y = scaled_height // 2 - height // 2
        image = image.crop((x, y, x + width, y + height))


        # Display image.
        self.disp.image(image)





if __name__ == "__main__":
    SCREEN_WIDTH = 320
    SCREEN_HEIGHT = 480

    root = tk.Tk()
    #root.geometry(f"{SCREEN_WIDTH}x{SCREEN_HEIGHT}")  # Set the window dimensions
    root.geometry("{}x{}".format(SCREEN_WIDTH, SCREEN_HEIGHT))
    app = App(root)
    root.mainloop()
