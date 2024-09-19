# Voice Activity Detection - Audio Player with Waveform and VAD

![CI](https://github.com/your-repository/voice-activity-detection/actions/workflows/ci.yml/badge.svg)

## Overview

**Voice Activity Detection** is an audio player application that visualizes audio waveforms and uses Voice Activity
Detection (VAD) to highlight where voice is detected in the audio file. It allows you to load `.wav` files, visualize
their waveform, and see sections of the audio that contain speech activity.

## Features

- Load and play `.wav` audio files.
- Visualize audio waveforms.
- Detect voice activity using WebRTC's VAD algorithm and highlight the segments of the audio with speech.
- Seek through the audio using a slider.
- Play/Pause functionality.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/repository/voice-activity-detection.git

2. Create and Activate a Virtual Environment

   ```bash
   cd voice_activity_detection/src
   pip install -r ../requirements.txt

3. Run the app:

   ```bash
   python main.py

* On Windows:

    * Create a virtual environment:

       ```bash
       python -m venv venv
       ```
    * Activate the virtual environment:

       ```bash
      venv\Scripts\activate
       ```
* On macOS/Linux:
    * Create a virtual environment:

       ```bash
       python3 -m venv venv
       ```
    * Activate the virtual environment:

       ```bash
       source venv/bin/activate
      ```

4. Install Dependencies

   Once the virtual environment is activated, install the required dependencies by running:

    ```bash
    pip install -r requirements.txt
    ```
   This will install all the necessary packages, including customtkinter, matplotlib, pygame, webrtcvad, and other
   required libraries.


5. Run the App

   Navigate to the src/ folder and run the application:

    ```bash
    cd src
    python main.py
    ```

   This will launch the Voice Activity Detection app, where you can load .wav files, visualize waveforms, and detect
   voice activity.


6. Deactivate the Virtual Environment

   Once you're done using the app, you can deactivate the virtual environment with:

    ```bash
    deactivate
    ```

    ```bash
    voice_activity_detection/
    │
    ├── src/
    │   ├── config/
    │   │   └── config.py
    │   ├── constants/
    │   │   └── app_constants.py
    │   ├── controllers/
    │   │   └── audio_controller.py
    │   ├── models/
    │   │   └── audio_model.py
    │   ├── views/
    │   │   └── audio_view.py
    │   ├── services/
    │   │   └── vad_service.py
    │   └── main.py
    │
    ├── README.md
    ├── requirements.txt
    └── .pylintrc

    ```

This command works on both Windows and macOS/Linux systems.
---

### Final Notes:

1. **Project Name**: The project is now renamed to **Voice Activity Detection**, and all related constants, window
   titles, and configuration are updated to reflect the new name.
2. **README.md**: It includes a description of the app, installation instructions, and a breakdown of the code
   structure.
3. **Pylint**: Run **Pylint** to ensure the project meets Python coding standards. You can update the `.pylintrc` file
   if needed.

This structure and setup make your project easier to maintain, more descriptive, and organized. Let me know if you need
more changes or help!
