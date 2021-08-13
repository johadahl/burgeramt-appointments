# Berlin Bürgeramt appointment finder

This tool finds the available appointment dates for the Berlin Bürgeramt. This script does not book appointments, it only finds them and logs them to a file and pushes a notification to the Mac OS Notification Center. 

The requests will return 419 after some time...

If you need an appointment as soon as possible, [there are better ways](http://allaboutberlin.com/guides/berlin-burgeramt-appointment).


# Usage:
## Prerequisites:
- This fork only works on OSX as it is integrated with the OSX Notification Center, so you'll get notifications when there is a free slot. 
Use any of the older versions if you don't want that feature. (Eg. https://github.com/Geekfish/burgeramt-appointments)

## Usage
1. Clone the repo

2. Install the requirements:
```shell
pip install -r requirements.txt
```

3. Run the script:
```shell
python appointments.py
```

4. Wait for notifications of an available time slot to show up and follow the link book it.
