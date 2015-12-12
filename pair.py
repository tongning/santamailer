import csv
import random
import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

fromname = "Firstname Lastname"
fromaddr = "12345@gmail.com"
email_password = "REDACTED"

class Participant(object):
    def __init__(self, fname, lname, email, misc_info_dict):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.misc_info = misc_info_dict
        self.gifter = None
        self.giftee = None
    def __str__(self):
        return self.fname + " " + self.lname

    def assign_gifter(self, person):
        self.gifter = person

    def assign_giftee(self, person):
        self.giftee = person

    def has_gifter(self):
        if self.gifter is not None:
            return True
        else:
            return False

    def has_giftee(self):
        if self.giftee is not None:
            return True
        else:
            return False


f = open('participants.csv')
csv_f = csv.reader(f)
csv_list = list(csv_f)
csv_list_filtered = list()
for row in csv_list:
    # Remove empty rows
    if row[0]:
        csv_list_filtered.append(row)

need_gifter = list()
need_giftee = list()
all_participants = list()
headers = csv_list_filtered[0]
csv_list_filtered.remove(headers)
for row in csv_list_filtered:
    # Create Participant objects and add them to a list
    first_name = row[0]
    last_name = row[1]
    email_addr = row[2]
    # Gather info in other columns in a dictionary
    misc_info = dict()
    for idx, val in enumerate(row):
        if idx >= 3:
            misc_info[headers[idx]] = row[idx]
    # Create new Participant object
    new_participant = Participant(first_name, last_name, email_addr, misc_info)
    # Add the new Participant to both need_gifter and need_giftee lists
    all_participants.append(new_participant)
    need_gifter.append(new_participant)
    need_giftee.append(new_participant)

while len(need_gifter) > 0 or len(need_giftee) > 0:
    # Randomly pick a gifter, and assign a giftee
    random_gifter = random.choice(need_giftee)
    random_giftee = random.choice(need_gifter)
    # Assign the giftee to the gifter

    random_gifter.assign_giftee(random_giftee)
    random_giftee.assign_gifter(random_gifter)
    # Gifter no longer needs a giftee and giftee no longer needs a gifter
    need_gifter.remove(random_giftee)
    need_giftee.remove(random_gifter)



# Everyone should have a gifter and a giftee now
# Check that this is the case
for participant in all_participants:
    if participant.has_giftee() and participant.has_gifter():
        print str(participant) + " will receive a gift from " + str(participant.gifter) \
        + " and give a gift to " + str(participant.giftee)
    else:
        print "A problem occurred while creating assignments. Exiting."
        sys.exit(2)

# Craft email messages
messages = list()
for participant in all_participants:
    toaddr = participant.email
    giftee_fname = participant.giftee.fname
    giftee_lname = participant.giftee.lname
    giftee_email = participant.giftee.email
    giftee_lunchpd = participant.giftee.misc_info['Lunch Pd']
    giftee_price_exceptions = participant.giftee.misc_info['Special exceptions to price range']
    giftee_surprise_option = participant.giftee.misc_info['Surprise me!']
    giftee_interests = participant.giftee.misc_info['Interests']
    giftee_requests = participant.giftee.misc_info['Requests']
    msg = MIMEMultipart()
    msg['From'] = fromname+" "+fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Your Secret Santa Recipient"
    body = """Hello %s,

Thanks for signing up for the Magnet 2016 Secret Santa! You have been randomly assigned a
person to whom you will be giving a gift. Below you will find the person's name, contact info,
and other relevant information.
--------------------------------
Name: %s %s
Email: %s
Lunch period: %s
Special exceptions to price range: %s
Surprise me: %s
Interests:
%s
Requests:
%s
--------------------------------

Have fun and happy holidays!

            """ % (participant.fname, giftee_fname,giftee_lname,giftee_email,giftee_lunchpd,giftee_price_exceptions,\
                                giftee_surprise_option,giftee_interests,giftee_requests)
    msg.attach(MIMEText(body, 'plain'))
    messages.append(msg)

# Write email preview file
emailfile = open("email_preview.txt", 'w')
emailfile.truncate()
for message in messages:
    emailfile.write(message.as_string())
emailfile.close()
print
print("Previews of the email messages have been saved to email_preview.txt.")
print("***PLEASE OPEN THIS FILE NOW AND INSPECT THE CONTENTS FOR ERRORS.***\n")
print("If they look good, type \"y\" and hit [Enter] to send immediately.")
print("(Typing anything else will abort the program.)\n\n")

confirmation = raw_input("Send emails now? ==>")
if confirmation == 'y':
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, email_password)
    for message in messages:
        text = message.as_string()
        server.sendmail(fromaddr, message['To'], text)
    server.quit()
else:
    print "Aborting."
    sys.exit(0)



