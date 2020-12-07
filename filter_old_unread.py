""" File: filter_old_unread.py
This script uses email_credentials to access the emails using IMAP.

This automated filter marks an email read if all three of these conditions are met:
1) a sender is part of the to_be_filtered list
2) the email is unread.
3) the email is older than 2 weeks.

email_credentials.py contains two variables: email_address & email_login.

Author: Paul Brockmann
"""
import datetime
import email
from email.header import decode_header
import email_credentials
import imaplib


def email_startup():
    """Signs into Email and returns imap object"""
    imap = imaplib.IMAP4_SSL('imap.gmail.com')
    # authenticate
    imap.login(email_credentials.email_user, email_credentials.email_pass)
    return imap


def get_unread_count(imap):
    """Returns current unread count"""
    status, response = imap.uid('search', None, 'UNSEEN')
    unread_msg_nums = response[0].split()
    return len(unread_msg_nums)


current_time = datetime.datetime.today()
days = 12
days_after = datetime.timedelta(days)
new_date = current_time - days_after
new_date = new_date.strftime("%d-%b-%Y")


imap = email_startup()
status, messages = imap.select('Inbox')
status, messages = imap.search(None, '(BEFORE "' + str(new_date) + '" UNSEEN)')
messages = messages[0].decode('UTF-8').split()

filtered_messages = len(messages)
initial_unread = get_unread_count(imap)
print(f'Processing {filtered_messages} unread emails from before {new_date}')
print("="*100)

for i in messages:
    # fetch the email message by ID
    res, msg = imap.fetch(str(i), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse bytes email into a message object
            msg = email.message_from_bytes(response[1])
            #print(msg.keys())

            # decode the email subject
            subject = decode_header(msg["Subject"])[0][0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode()

            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)

            # decode email Date
            Date, encoding = decode_header(msg.get("Date"))[0]
            if isinstance(From, bytes):
                Date = Date.decode(encoding)

            print("Subject: ", subject)
            print("From: ", From)
            print("Date: ", Date)

            print("="*100)
            #x = input('Continue? ')


post_unread = get_unread_count(imap)
print(f'Processed Emails: {initial_unread - post_unread}')
print(f'After processing, there are {post_unread} unread emails.')


# close the connection and logout
imap.close()
imap.logout()



