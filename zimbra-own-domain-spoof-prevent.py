#!/usr/bin/env python
# Checks for /opt/zimbra/postfix/conf/sender_access_new and domains Zimbra has configured,
# and if there is a mismatch, updates the file and restarts ZCS MTA
# - run as zimbra user
# - Insert this line: "check_sender_access lmdb:/opt/zimbra/postfix/conf/sender_access_new"
#   in /opt/zimbra/conf/zmconfigd/smtpd_sender_restrictions.cf, above the line that has
#   "regexp:/opt/zimbra/common/conf/tag_as_foreign.re%%"
# - Add to crontab for periodic checks

import sys
import argparse
from argparse import RawTextHelpFormatter
from subprocess import Popen, PIPE, call

def run(command):
    p = Popen(command , shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    #print(command)
    #print(out)
    return out

def main():
    zcs_domains = run("zmprov gad")
    zcs_domains = zcs_domains.split()
    postfix_domains = run("cat /opt/zimbra/postfix/conf/sender_access_new|awk '{ print $1 }'")
    postfix_domains = postfix_domains.split()
    if set(zcs_domains) != set(postfix_domains):
        print("Updating postfix sender_access_new")
        with open('/opt/zimbra/postfix/conf/sender_access_new', 'w') as f:
            for i in zcs_domains:
                f.write("%s 550 YOU ARE NOT ME.\n" % str(i))
        run("postmap /opt/zimbra/postfix/conf/sender_access_new")
        run("zmmtactl stop")
        run("zmmtactl start")

if __name__ == '__main__':
    main()
