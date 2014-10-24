#!/usr/bin/python

import string
import math
import pickle
import sys
import os
import subprocess

MONITOR_HOME='/home/monitor'
MONITOR_VAR=MONITOR_HOME+'/var'
MONITOR_TMP=MONITOR_HOME+'/tmp'

pid=sys.argv[1]
hcfg = open(MONITOR_TMP+'/'+pid+'.hostcfg','r')
scfg = open(MONITOR_TMP+'/'+pid+'.svccfg','r')

hostconfig={}
for line in hcfg:
    if line == '':
        pass
    hostlist=line.split('|')
    cust=hostlist[0]
    host=hostlist[1]
    key=cust+'|'+host
    hostconfig[key]=1

enterprise_state={}

for line in scfg:
    if line == '':
        pass
    svclist=line.split('|')
    cust=svclist[0]
    host=svclist[1]
    svc=svclist[2]
    svc_threshold_max=svclist[3]
    svc_contact_groups=svclist[4]
    svc_retry_interval=svclist[5].rstrip()
    svc_notification_interval=svclist[6].rstrip()
    svc_SMS_status=svclist[7].rstrip()
    svc_email_status=svclist[8].rstrip()
    key=cust+'|'+host
####IF A HOST IS COMMENTED OUT IN /HOME/MONITOR/ETC/HOSTS.CFG THEN IT WILL NOT BE MONITORED####
    if not hostconfig.has_key(key):
        pass
    else:
        status=subprocess.Popen('cat '+MONITOR_VAR+'/'+cust+'/'+host+'/'+svc, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        statlist=status.split('|')
        svc_state=statlist[0]
	try:
            svc_remote_date=statlist[1].rstrip()
	except IndexError:
	    pass
        if len(statlist) > 2:
            svc_output=statlist[2]
            svc_exit_status=statlist[3].rstrip()
        else:
            svc_output=''
            svc_exit_status=''
        current_date_epoch=subprocess.Popen('date +%s', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        remote_date_epoch=subprocess.Popen('date -d "'+svc_remote_date+'" +"%s"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        threshold=math.fabs(string.atof(current_date_epoch) - string.atof(remote_date_epoch))
        if threshold > string.atof(svc_threshold_max):
           svc_state='STALE'
           NOTIFY='1'
           status=svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+svc_remote_date+'|'+str(threshold)+'|'+svc_contact_groups+'|'+svc_retry_interval+'|'+NOTIFY+'|'+svc_notification_interval+'|'+svc_SMS_status+'|'+svc_email_status
        else:
           if svc_state == 'CRITICAL' or svc_state == 'WARNING':
               NOTIFY='1'
               status=svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+svc_remote_date+'|'+str(threshold)+'|'+svc_contact_groups+'|'+svc_retry_interval+'|'+NOTIFY+'|'+svc_notification_interval+'|'+svc_SMS_status+'|'+svc_email_status
           else:
               NOTIFY='0'
               status=svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+svc_remote_date+'|'+str(threshold)+'|'+svc_contact_groups+'|'+svc_retry_interval+'|'+NOTIFY+'|'+svc_notification_interval+'|'+svc_SMS_status+'|'+svc_email_status
        if svc == 'link_status':
            svc='link'
        site=cust+'|'+host+'|'+svc
        if hostconfig.has_key(key):
           enterprise_state[site]=status
        print site+'|'+enterprise_state[site]
