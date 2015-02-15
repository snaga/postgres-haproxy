#!/bin/sh

PATH=/usr/pgsql-9.4/bin:$PATH
export PATH

PGDATA=/tmp/pgdata/master1

ps auxx | grep $PGDATA |grep -v grep | awk '{ print $2 }' | xargs kill

rm -rf $PGDATA

initdb -D $PGDATA --no-locale -E utf-8

cp -v postgresql.conf pg_hba.conf $PGDATA

pg_ctl -w -D $PGDATA start -o "-p 5432"
