# ProcrastiMate
ProcrastiMate is a desktop application designed to help users manage procrastination and foster productive habits by controlling computer access based on a user’s daily routine. The application integrates a customizable scheduler and blocker system that ensures users remain focused on their tasks.

Features
Routine Scheduling: Create and manage daily routines with specific tasks and schedules.
Distraction Blocking: Block access to distracting applications during scheduled tasks to enhance productivity.
Real-Time Notifications: Receive notifications if attempting to access blocked programs during a task period.
Task Management: View, modify, and remove tasks from a user-friendly interface.
Persistent Data: Tasks and schedules are saved and persist between application sessions.
Technologies and Libraries Used
Python: The primary programming language used for the application’s backend logic.
Tkinter: Utilized for creating the graphical user interface (GUI) of the application.
Pygetwindow, Pyautogui, ctypes: Libraries for system management, including window handling and application control.
Schedule: For scheduling tasks and managing routine timings.
Plyer: For sending cross-platform notifications.
Setup and Installation

Clone the Repository:

git clone https://github.com/yourusername/procrastimate.git
Navigate to the Project Directory:


cd procrastinate
Install Dependencies:
Create a virtual environment and install the required packages:


python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt
Run the Application:


python main.py
