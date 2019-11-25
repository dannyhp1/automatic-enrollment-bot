# Automatic Enrollment Bot
Nowadays, courses at universities tend to fill up before a student has the opportunity to enroll. With the automatic enrollment bot, students will have a tool to automate their enrollment process.

A student provides the bot with specific courses they'd like to monitor and the bot will take care of everything else. When a course is full, the bot will continually monitor the status of that course until it becomes open. When the course is open, it will automatically enroll the student in the course and send them a mobile notification upon successful enrollment.

# Disclaimer
The bot requires a user to provide their student information in a local text file. Although the text file is local, this is still be unsafe. In addition, the bot was made for both education purposes and for my own personal use. Therefore, before using the bot, please understand that **you are using it at your own risk**. If anything occurs, I take no responsibility.

# Getting Started
- You will need Python3 in order to start the bot.
- Create two files and fill them out with your information: user_information.txt and twilio_information.txt.
- Please look at 'start.py' and modify it based on your own needs. Please read the comments as they are important.
- To start the bot, please run the following script: `python3 start.py`