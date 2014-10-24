#!/bin/bash

#set -x

MONITOR_HOST=10.1.1.4
MONITOR_HOME=/home/monitor
MONITOR_BIN=${MONITOR_HOME}/bin
MONITOR_VAR=${MONITOR_HOME}/var
MONITOR_TMP=${MONITOR_HOME}/tmp
MONITOR_CONF=${MONITOR_HOME}/etc
MONITOR_LOG=${MONITOR_HOME}/logs
echo "-----------------------------------------------------------------------------------------------------------------------------------------------------"
echo "CUST	HOST	SVC	STATUS		OPTIONAL_OUTPUT"
echo "-----------------------------------------------------------------------------------------------------------------------------------------------------"

cp ${MONITOR_CONF}/hosts.cfg ${MONITOR_TMP}/$$.1
cp ${MONITOR_CONF}/services.cfg ${MONITOR_TMP}/$$.2

arg_string=$*
total_args=$#
pid=$$

if [[ $arg_string =~ "--alert" ]]
then
	if [ $total_args -eq 4 ]; then
		cust=$1
		host=$2
		svc=$3
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep $host | grep $svc | grep "|" > ${MONITOR_TMP}/$$.svccfg
	elif [ $total_args -eq 3 ]; then
		cust=$1
		host=$2
		svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.svccfg
	elif [ $total_args -eq 2 ]; then
		cust=$1
		host='none'
		svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep "|" > ${MONITOR_TMP}/$$.svccfg
	else
		cust='none'
		host='none'
		svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.svccfg
	fi
	
	${MONITOR_BIN}/monitor_enterprise.py $pid > ${MONITOR_TMP}/$$.mstate
	cat ${MONITOR_TMP}/$$.mstate | awk -F"|" '{print $1"\t"$2"\t"$3"\t"$4"\t\t"$5}'
	cat ${MONITOR_TMP}/$$.mstate > ${MONITOR_TMP}/enterprise_state
	
	cp ${MONITOR_CONF}/contact-groups.cfg ${MONITOR_TMP}/$$.3
	cp ${MONITOR_CONF}/contacts.cfg ${MONITOR_TMP}/$$.4
	
	cat ${MONITOR_TMP}/$$.3 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.contact_grps
	cat ${MONITOR_TMP}/$$.4 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.contacts
	if [ ! -f ${MONITOR_TMP}/OK.dict ]; then
		touch ${MONITOR_TMP}/OK.dict        
	fi
	if [ ! -f ${MONITOR_TMP}/PROBLEM.dict ]; then
		touch ${MONITOR_TMP}/PROBLEM.dict      
	fi
	${MONITOR_BIN}/notifier.py $pid | tee -a ${MONITOR_LOG}/monitor.log
	
else
	if [ $total_args -eq 3 ]; then
		cust=$1
                host=$2
                svc=$3
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep $host | grep $svc | grep "|" > ${MONITOR_TMP}/$$.svccfg
	elif [ $total_args -eq 2 ]; then
		cust=$1
                host=$2
		svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep $host | grep "|" > ${MONITOR_TMP}/$$.svccfg
	elif [ $total_args -eq 1 ]; then
		cust=$1
		host='none'
		svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep $cust | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep $cust | grep "|" > ${MONITOR_TMP}/$$.svccfg
	else
                cust='none'
                host='none'
                svc='none'
		cat ${MONITOR_TMP}/$$.1 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.hostcfg
        	cat ${MONITOR_TMP}/$$.2 | grep -v '#' | grep "|" > ${MONITOR_TMP}/$$.svccfg
        fi
	${MONITOR_BIN}/monitor_enterprise.py $pid > ${MONITOR_TMP}/$$.mstate
	cat ${MONITOR_TMP}/$$.mstate | awk -F"|" '{print $1"\t"$2"\t"$3"\t"$4"\t\t"$5}'
fi

echo "-----------------------------------------------------------------------------------------------------------------------------------------------------"

echo "Cleaning up temporary files from cuda2:${MONITOR_TMP}"
rm -f ${MONITOR_TMP}/$$.*
#rm -f ${MONITOR_TMP}/enterprise_state
