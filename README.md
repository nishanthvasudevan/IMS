Infrastructure Monitoring System
================================

This is a monitoring system written mostly using Python and Bash.  
Assets to be monitored send their service status to predefined location for that asset.  
Service status is a string of the form "SERVICE STATUS|`date`|STATUS DESCRIPTION|STATUSCODE".  
bin/enterprise_monitor.sh runs from cron every 60 seconds.  
The system is capable of sending alerts as a text message or email. New alert delivery system can added.  
It can send service recovery alerts as well.
The entire system is tunable using config files in conf/
Alert recipients, assets and services to be monitored, alert frequency etc can be controlled from the config files.  
I have used this in production since early 2010.
