#!/bin/sh

_PGNAME=$1
_PGDATA=$2
_PGPORT=$3

if [ -s $_PGPORT ]; then
    echo "Usage: $0 <PGNAME> <PGDATA> <PGPORT>"
    exit 0
fi

# input parameters:
#  - Slave PGDATA
#  - Master Hostname/IP
#  - Master Port
#  - Master Username
#  - Slave (App)Name
#  - Slave Port

PATH=/usr/pgsql-9.4/bin:$PATH
export PATH

_PID=`ps auxx | grep $_PGDATA | grep -v grep | grep -v $0 | awk '{ print $2 }'`

if [ "$_PID"x != "x" ]; then
    echo kill $_PID
    kill $_PID
fi

echo rm -rf $_PGDATA
rm -rf $_PGDATA

# initdb -D /tmp/pgdata2 --no-locale -E utf-8
# cp -v postgresql.conf pg_hba.conf /tmp/pgdata2

psql -h 127.0.0.1 -c 'checkpoint' postgres

echo pg_basebackup -h 127.0.0.1 -U snaga -D $_PGDATA --xlog --progress --verbose
pg_basebackup -h 127.0.0.1 -U snaga -D $_PGDATA --xlog --progress --verbose

cat <<EOF > recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=127.0.0.1 port=5432 user=snaga application_name=${_PGNAME}'
EOF

cat recovery.conf
mv -v recovery.conf $_PGDATA

pg_ctl -w -D $_PGDATA start -o "-p $_PGPORT"
