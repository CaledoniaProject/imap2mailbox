#!/usr/bin/env python

import os
import sys
import imaplib
from pprint import pprint

import argparse

parser = argparse.ArgumentParser(description = 'IMAP mailbox dump tool')

parser.add_argument('-s', action = "store", dest = "server",   required = True, help = "mail server address")
parser.add_argument('-u', action = "store", dest = "username", required = True)
parser.add_argument('-p', action = "store", dest = "password", required = True)
parser.add_argument('-d', action = "store", dest = "maildir",  required = True)

class Mailbox:
    def __init__(self, **kwargs):
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.server   = kwargs['server']
        self.maildir  = kwargs['maildir']

        self.login()
        self.create_maildir()

    def login(self):
        print '[-] Logging in ..'
        self.M = imaplib.IMAP4_SSL(self.server)
        self.M.login(self.username, self.password)

    def create_maildir(self):
        if os.path.exists(self.maildir):
            print '[!] warning: directory', self.maildir, 'already exists'

        for subdir in ['tmp', 'cur', 'new']:
            newdir = self.maildir + '/' + subdir

            print '    - mkdir', subdir
            if not os.path.exists(newdir):
                os.makedirs(self.maildir + '/' + subdir)
            elif not os.path.isdir(newdir):
                raise newdir + ' exists and is not a directory'

    def download(self, box = 'INBOX'):
        status, data = self.M.select(box)
        if status != 'OK':
            print '[!] Failed to open mailbox:', status, data
            return -1

        status, data = self.M.search(None, 'ALL')
        if status != 'OK':
            print '[!] Failed to search ' + box + ': ', status, data
            return -1

        ids = data[0].split()
        print '[-] Number of emails:', len(ids)

        for mail_id in ids:
            status, data = self.M.fetch(mail_id, '(RFC822)')
            if status != 'OK':
                print '[!] Failed to fetch message #' + mail_id
            else:
                outfile = self.maildir + '/cur/' + mail_id
                with open(outfile, 'wb') as f:
                    f.write(data[0][1])

                print '    - letter', mail_id, 'Saved'

        print '[-] You may open mailbox like this'
        print '    mutt -f', self.maildir

if __name__ == '__main__':
    args = parser.parse_args()

    m = Mailbox(
        username = args.username, 
        password = args.password, 
        server   = args.server, 
        maildir  = args.maildir)
    m.download()


