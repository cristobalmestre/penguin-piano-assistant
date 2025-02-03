# penguin-piano-assistant
Piano Assistant on a Raspberry Pi

Proof of concept: Improve your children's Piano Skills with this beautiful 3D printed penguin
Watch the video to learn more: https://www.youtube.com/watch?v=-PIMhoII1Og

**Piano Assitant Execute instructions and must-knows**

All of the installed libraries can be found at the config_assitant.py file, plus detailed instructions for instaling the compiling libraries.
The program was tested with Python 3.11.4 on a Raspberry Pi 4 with Raspian Os.

1. To run the code you need to download the five ".py" files and unzip the "Piano Learning Assistant Project folders.zip" file in the same folder.
2. The config_assitant.py file controls the name of the working directory. You must update it there.
3. Execute the "execute_sequence-py" file, that will use all the others. All libraries need to end up properly installed for the whole program to run correctly.


# penguin-piano-assistant
A Raspberry Pi-based piano learning assistant for children 🐧🎹  

This project is a **proof of concept** for an interactive **piano learning assistant** enclosed in a **3D-printed penguin**. It helps children **improve their piano skills** through **real-time feedback**, **MIDI-based analysis**, and a **touchscreen interface**.

📽️ **Watch the demo video:** [YouTube Link](https://www.youtube.com/watch?v=-PIMhoII1Og)

---

## **Features**
✅ **Interactive feedback:** Detects and scores played notes based on a predefined MIDI file.  
✅ **Real-time assessment:** Analyzes pitch accuracy and timing consistency.  
✅ **Touchscreen interface:** Displays step-by-step instructions and performance results.  
✅ **Raspberry Pi-powered:** Designed to run on a **Raspberry Pi 4** with a touchscreen.  
✅ **3D-printed penguin case:** Makes learning fun for kids! 🐧  

---

## **Getting Started**

### **1️⃣ Installation & Setup**
Before running the project, ensure your **Raspberry Pi 4** is configured with **Python 3.11.4** and all necessary dependencies.

### **2️⃣ Prerequisites**
1. **Enable SPI on Raspberry Pi** (Required for touchscreen functionality).
2. Install required libraries. See `config_assistant.py` for a full list.

Run the following commands on your Raspberry Pi terminal:

```sh
sudo apt-get update
sudo apt-get install portaudio19-dev libasound2-dev libpulse-dev \
    libsndfile-dev libsamplerate0-dev libssl-dev \
    python3-pil python3-tk tk-dev python3-pandas \
    python3-pyaudio python3-aubio
pip install -r requirements.txt
```

### **3️⃣ Setting Up the Project**
1. **Clone the repository** or **download the project files**.
2. Ensure all **Python scripts** (`.py` files) and required **folders** are in the same directory.
3. **Update the working directory** inside `config_assistant.py`:
   ```python
   new_directory = "/home/pi/penguin_piano_assistant"
   ```
4. **Run the program** by executing:
   ```sh
   python3 execute_sequence.py
   ```

---

## **Project Files Overview**
📂 **Main Components:**
- `execute_sequence.py` → Runs the main program, executing required scripts.
- `graphic_interphase_for_pi.py` → Handles the touchscreen GUI.
- `Read_MIDI_record_compare.py` → Converts a MIDI file into a comparable format.
- `Comparison_scoring.py` → Evaluates and scores piano performance.
- `config_assistant.py` → Manages system settings and dependencies.

📂 **Data & Assets:**
- `MIDI Files/` → Contains MIDI songs for comparison.
- `MIDI_to_CSV_songs/` → Stores preprocessed songs in CSV format.
- `player_recorded_tunes/` → Saves user recordings for analysis.
- `Screens/` → Stores UI images displayed on the touchscreen.

---

## **How It Works**
1️⃣ **Select a song** (default: "Jingle Bells").  
2️⃣ **MIDI file is analyzed** and converted into a reference format.  
3️⃣ **User plays the song** on a real piano.  
4️⃣ **System records the notes**, analyzes pitch and timing.  
5️⃣ **Feedback is displayed** on the touchscreen, showing score and improvements.  

---

## **License**
This project is licensed under the **GNU General Public License v3.0**.  

See the `LICENSE` file for details.  
More about the GPL-3.0: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---

## **Contributing**
Want to improve **penguin-piano-assistant**? Feel free to:
- Open an **Issue** for bug reports or feature suggestions.
- Submit a **Pull Request** with enhancements.

---

## **Future Improvements**
🔹 Support for additional songs.  
🔹 Real-time AI-based feedback with machine learning.  
🔹 Wireless integration with tablets and mobile devices.  

---

**🐧🎹 Happy Piano Learning!** 🚀  