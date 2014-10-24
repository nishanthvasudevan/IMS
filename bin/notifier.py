#!/usr/bin/python

import os
import sys
import subprocess
import math
import cPickle
import string

non_critical_hour = 0
hour = subprocess.Popen('date +%H', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

MONITOR_HOME='/home/monitor'
MONITOR_VAR=MONITOR_HOME+'/var'
MONITOR_TMP=MONITOR_HOME+'/tmp'
MONITOR_CONF=MONITOR_HOME+'/etc'
env={}

def notify(message_contents,contact_grp):
	contact_list = subprocess.Popen('cat '+MONITOR_CONF+'/contact-groups.cfg | grep '+contact_grp+' | grep -v \'#\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
	contact_lists = contact_list.split('|')
	contact_list_alias = contact_lists[1]
	contact_list = contact_lists[2].split(',')
	for contacts_line in contact_list:
		contact = subprocess.Popen('cat '+MONITOR_CONF+'/contacts.cfg | grep '+contacts_line+' | grep -v \'#\'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
		try:
			contacts = contact.split('|')
			contact_name = contacts[1]
			email_id = contacts[2]
			msisdn = contacts[3].rstrip()
			sendmail(email_id,message_contents)
			sendChat(email_id,message_contents)
			sendSMS(msisdn,message_contents)
		except IndexError:
			pass
	sys.stdout.write('\n')

def sendmail(email_id, message_contents):
	content = message_contents.split('|')
	site = content[0]+'-'+content[1]
	svc = content[2]
	svc_state = content[3]
	svc_output = content[4]
	remote_date = content[6]
	sms_status = content[8]
	email_status = content[9]

	if svc_state == 'OK':	
		subject = 'RECOVERY: '+svc+' '+site
	else:
		subject = 'PROBLEM: '+svc+' '+site
	if svc == 'link' and svc_state == 'STALE':
		message = site+' is unreachable. Last update received at '+remote_date
	elif svc == 'link' and svc_state == 'OK':
		message = site+' is reachable. Last update received at '+remote_date
	else:
		message = site+' - '+svc+' is '+svc_state+':'+svc_output+':'+remote_date
	if email_status == 'no-email':
		sys.stdout.write('no-email:')
	else:
		sys.stdout.write(email_id+':')
		subprocess.Popen('echo "'+message+'" | /bin/mailx -s "'+subject+'" '+email_id+'', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def sendSMS(msisdn, message_contents):
	content = message_contents.split('|')
        site = content[0]+'-'+content[1]
        svc = content[2]
        svc_state = content[3]
        svc_output = content[4]
        remote_date = content[6]
	sms_status = content[8]
	email_status = content[9]
	env["JAVA_HOME"] = "/usr/java"
        env["PATH"] = "/usr/java/bin:/home/monitor/bin:/home/monitor/bin/alerts:/usr/sbin:/sbin:/usr/local/bin:/ubona/bin:/root/svnlocal/asr/trunk/bin:/usr/bin"

	if svc == 'link' and svc_state == 'STALE':
                message = site+' is unreachable. Last update received at '+remote_date
        elif svc == 'link' and svc_state == 'OK':
                message = site+' is reachable. Last update received at '+remote_date
        else:
                message = site+' - '+svc+' is '+svc_state+':'+svc_output+':'+remote_date

	if string.atof(hour) < string.atof(non_critical_hour):
		print "NON_CRITICAL_HOUR, SMS WILL NOT BE SENT"
	else:
		if sms_status == 'no-sms':
			sys.stdout.write('no-sms,')
		else:
			sys.stdout.write(msisdn+',')
			subprocess.Popen('/home/monitor/bin/alerts/sendSms.sh '+msisdn+' "'+message+'"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def sendChat(email_id, message_contents):
        content = message_contents.split('|')
        site = content[0]+'-'+content[1]
        svc = content[2]
        svc_state = content[3]
        svc_output = content[4]
        remote_date = content[6]
        sms_status = content[8]
        email_status = content[9]
	env["JAVA_HOME"] = "/usr/java"
        env["PATH"] = "/usr/java/bin:/home/monitor/bin:/usr/sbin:/sbin:/usr/local/bin:/ubona/bin:/root/svnlocal/asr/trunk/bin:/usr/bin"

        if svc == 'link' and svc_state == 'STALE':
                message = site+' is unreachable. Last update received at '+remote_date
        elif svc == 'link' and svc_state == 'OK':
                message = site+' is reachable. Last update received at '+remote_date
        else:
                message = site+' - '+svc+' is '+svc_state+':'+svc_output+':'+remote_date

                if email_status == 'no-email':
                        sys.stdout.write('no-email,')
                else:
                        sys.stdout.write(email_id+',')
                        subprocess.Popen('/home/monitor/bin/alerts/sendAlertOverGoogleChat.sh '+email_id+' "'+message+'"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


pid=sys.argv[1]
current_date = subprocess.Popen('date', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0].rstrip()

state=open(MONITOR_TMP+'/enterprise_state','r+')

PROBLEM_DICT = open(MONITOR_TMP+'/PROBLEM.dict','r')
OK_DICT = open(MONITOR_TMP+'/OK.dict','r')

try:
        OK_dict=cPickle.load(OK_DICT)
except EOFError:
        OK_dict={}

try:
        PROBLEM_dict=cPickle.load(PROBLEM_DICT)
except EOFError:
        PROBLEM_dict={}

OK_DICT.close()
PROBLEM_DICT.close()

#To be used later for checking if old enterprise status has a key that is not in the new enterprise status. i.e., to check if a service has recovered

for line in state:
        if line == '':
                pass
        histlist = line.split('|')
        cust = histlist[0]
        host = histlist[1]
        svc = histlist[2]
        svc_state = histlist[3]
        svc_output = histlist[4]
        svc_exit_status = histlist[5]
        remote_date = histlist[6]
        threshold = histlist[7]
        contact_grp = histlist[8]
	#if host == 'tyan':
		#contact_grp = 'test-admins'
		
        retry_interval = histlist[9]
        notify_flag = histlist[10].rstrip()
	svc_notification_interval = histlist[11].rstrip()
	sms_status = histlist[12].rstrip()
	email_status = histlist[13].rstrip()
        
	site = cust+'|'+host
        key = cust+'|'+host+'|'+svc
        
        if svc_state == 'WARNING' or svc_state == 'CRITICAL' or svc_state == 'STALE':
		try:
                        del OK_dict[key]
                except KeyError:
                        pass
		try:
			retry_interval = PROBLEM_dict[key].split('|')[9]
			notify_flag = PROBLEM_dict[key].split('|')[10]
		except KeyError:
			pass
               	PROBLEM_dict[key]=cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+contact_grp+'|'+retry_interval+'|'+notify_flag+'|'+svc_notification_interval+'|'+sms_status+'|'+email_status
        else:
                OK_dict[key]=cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+contact_grp+'|'+str(retry_interval)+'|'+notify_flag+'|'+svc_notification_interval+'|'+sms_status+'|'+email_status


PROBLEM_DICT = open(MONITOR_TMP+'/PROBLEM.dict','w')
OK_DICT = open(MONITOR_TMP+'/OK.dict','w')

#FOLLOWING CODE DECIDES WHEN TO SEND NOTIFICATIONS

for PROBLEM_key in PROBLEM_dict.keys():
	if OK_dict.has_key(PROBLEM_key):
  		OK_remote_date = OK_dict[PROBLEM_key].split('|')[6]
		PROBLEM_remote_date = PROBLEM_dict[PROBLEM_key].split('|')[6]
		OK_remote_date_epoch = subprocess.Popen('date -d "'+OK_remote_date+'" +"%s"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
		PROBLEM_remote_date_epoch = subprocess.Popen('date -d "'+PROBLEM_remote_date+'" +"%s"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
		diff = string.atof(PROBLEM_remote_date_epoch) - string.atof(OK_remote_date_epoch)
		cust = OK_dict[PROBLEM_key].split('|')[0]
                host = OK_dict[PROBLEM_key].split('|')[1]
                svc = OK_dict[PROBLEM_key].split('|')[2]
                svc_state = OK_dict[PROBLEM_key].split('|')[3]
                svc_output = OK_dict[PROBLEM_key].split('|')[4]
                svc_exit_status = OK_dict[PROBLEM_key].split('|')[5]
                remote_date = OK_dict[PROBLEM_key].split('|')[6]
                threshold = OK_dict[PROBLEM_key].split('|')[7]
                contact_grp = OK_dict[PROBLEM_key].split('|')[8]
		sms_status = OK_dict[PROBLEM_key].split('|')[12]
		email_status = OK_dict[PROBLEM_key].split('|')[13]
                message_contents = cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+sms_status+'|'+email_status
		problem_svc = PROBLEM_dict[PROBLEM_key].split('|')[2]
		problem_svc_state = PROBLEM_dict[PROBLEM_key].split('|')[3]
		if string.atof(PROBLEM_remote_date_epoch) < string.atof(OK_remote_date_epoch):
   			PROBLEM_retry_interval = PROBLEM_dict[PROBLEM_key].split('|')[9]
			PROBLEM_svc_state = PROBLEM_dict[PROBLEM_key].split('|')[3]
			if string.atof(PROBLEM_retry_interval) <= 0:
				if problem_svc_state == 'STALE' and problem_svc == 'link':
					sys.stdout.write(current_date+', RECOVERY-NOTIFICATION: '+contact_grp+' NOTIFIED. MESSAGE = '+message_contents+' TO THE FOLLOWING EMAIL/MSISDN ')
					notify(message_contents,contact_grp)
				elif problem_svc_state == 'STALE' and problem_svc != 'link':
					print current_date+', INFO:'+PROBLEM_key+' HAS RECOVERED FROM STALENESS. NOTIFICATION NOT REQUIRED.'
				elif problem_svc_state == 'CRITICAL' or problem_svc_state == 'WARNING':
					sys.stdout.write(current_date+', RECOVERY-NOTIFICATION: '+contact_grp+' NOTIFIED. MESSAGE = '+message_contents+' TO THE FOLLOWING EMAIL/MSISDN ')
					notify(message_contents,contact_grp)
				del PROBLEM_dict[PROBLEM_key]
			else:
				del PROBLEM_dict[PROBLEM_key]
	else:
		cust = PROBLEM_dict[PROBLEM_key].split('|')[0]
                host = PROBLEM_dict[PROBLEM_key].split('|')[1]
                svc = PROBLEM_dict[PROBLEM_key].split('|')[2]
                svc_state = PROBLEM_dict[PROBLEM_key].split('|')[3]
                svc_output = PROBLEM_dict[PROBLEM_key].split('|')[4]
                svc_exit_status = PROBLEM_dict[PROBLEM_key].split('|')[5]
                remote_date = PROBLEM_dict[PROBLEM_key].split('|')[6]
                threshold = PROBLEM_dict[PROBLEM_key].split('|')[7]
                contact_grp = PROBLEM_dict[PROBLEM_key].split('|')[8]
                retry_interval = PROBLEM_dict[PROBLEM_key].split('|')[9]
                notify_flag = PROBLEM_dict[PROBLEM_key].split('|')[10]
		svc_notification_interval = PROBLEM_dict[PROBLEM_key].split('|')[11]
		sms_status = PROBLEM_dict[PROBLEM_key].split('|')[12]
		email_status = PROBLEM_dict[PROBLEM_key].split('|')[13]
                message_contents = cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+sms_status+'|'+email_status
                retry_interval = string.atof(retry_interval) - 1
		next_retry_interval = retry_interval % string.atof(svc_notification_interval)
                if retry_interval == 0 or next_retry_interval == 0:
			if svc != 'link' and svc_state == 'STALE':
				print current_date+', WARNING:'+cust+'|'+host+'|'+svc+' is STALE. LAST UPDATE RECEIVED AT '+remote_date
                        	PROBLEM_dict[PROBLEM_key] = cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+contact_grp+'|'+str(retry_interval)+'|'+str(notify_flag)+'|'+svc_notification_interval+'|'+sms_status+'|'+email_status
			else:
                        	sys.stdout.write(current_date+', PROBLEM-NOTIFICATION: '+contact_grp+' NOTIFIED. MESSAGE = '+message_contents+' TO THE FOLLOWING EMAIL/MSISDN ')
                        	notify(message_contents,contact_grp)
                        	notify_flag = string.atof(notify_flag) - 1
                        	PROBLEM_dict[PROBLEM_key] = cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+contact_grp+'|'+str(retry_interval)+'|'+str(notify_flag)+'|'+svc_notification_interval+'|'+sms_status+'|'+email_status
                else:
                        PROBLEM_dict[PROBLEM_key] = cust+'|'+host+'|'+svc+'|'+svc_state+'|'+svc_output+'|'+svc_exit_status+'|'+remote_date+'|'+threshold+'|'+contact_grp+'|'+str(retry_interval)+'|'+notify_flag+'|'+svc_notification_interval+'|'+sms_status+'|'+email_status



cPickle.dump(OK_dict,OK_DICT)
cPickle.dump(PROBLEM_dict,PROBLEM_DICT)

OK_DICT.close()
PROBLEM_DICT.close()
