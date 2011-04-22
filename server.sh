#!/bin/bash

case "$2" in
    9001|9002|9003|9004)

        case "$1" in
            start)
                START_SCRIPT_PATH=`pwd`/website.py
                /usr/bin/env python $START_SCRIPT_PATH --port=$2 --daemon
                ;;
            stop)
                ps aux | egrep 'website[.]py' | egrep $2 | awk '{ print $2 }' | xargs kill -9;
                ;;
            restart)
                $0 stop $2
                $0 start $2
                ;;
            *)
                N=`pwd`/$NAME
                echo "Usage: $N {start|stop|restart} {9001|9002|9003|9004}" >&2
                exit 1
                ;;
        esac
        ;;

    *)
        N=`pwd`/$NAME
        echo "Usage: $N {start|stop|restart} {9001|9002|9003|9004}" >&2
        exit 1
        ;;
esac