#! /bin/bash

# Resolve links - $0 may be a softlink
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

#get shell full path
cd $PRGDIR
PRG_FULL_DIR=`pwd`
cd - >/dev/null

ROOT_DIR=$PRG_FULL_DIR

backup_file()
{
    [ -f ${1} ] &&    cp -f ${1} ${1}.bak
}

#
# $1 in file
# $2 target file
subst()
{
    f=$1
    real_f=$2
    echo "create  $real_f from $f"
    sed  \
	-e "s&@ROOT_DIR@&$ROOT_DIR&g" \
	$f > $real_f
	
    
}

cd $ROOT_DIR

in_file_list=`find $PRGDIR -name "*.in"`
for f in $in_file_list ; do
    real_f=${f%.*}
    backup_file $real_f
    subst $f  $real_f
done
