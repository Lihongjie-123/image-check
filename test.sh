#!/bin/bash

PRG="$0"
while [ -h "$PRG" ]; do
        ls=`ls -ld "$PRG"`
        link=`expr "$ls" : '.*-> \(.*\)$'`
        if expr "$link" : '.*/.*' > /dev/null; then
                PRG="$link"
        else
                PRG=`dirname "$PRG"`/"$link"
        fi
        done
PRGDIR=`dirname "$PRG"`

assert_empty()
{
   if [ "$1" != "" ]; then
       time_now=`date "+%D %T"`
       echo "[$time_now] $2 failed, exit"
       exit 1
   else
       time_now=`date "+%D %T"`
       echo "[$time_now] $2 success"   
   fi
}

if [ ! -d /opt/python-common ];then
    echo "python common not found , exit"
    exit 
fi

#full path
cd $PRGDIR/
PRGDIR=`pwd`
cd - >/dev/null

#TODO 增加test.sh的测试用例