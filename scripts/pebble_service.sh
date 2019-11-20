#!/bin/bash
## Copyright 2019 Flavio Garcia
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
##
## pebble_service.sh    This shell script takes care of starting and stopping
##                      pebble.
##
## description: Peeble service runner.
## processname: pebble_service.sh

## Author: Flavio Garcia <piraz@cadnango.org>

AWK_CMD="/usr/bin/awk"
CURL_CMD="/usr/bin/curl"
PWD_PATH="/usr/bin/pwd"

ORIGINAL_PATH=$PWD_PATH
SCRIPT_PATH=$(dirname $0)
SCRIPT_NAME=$(basename $0)

SCRIPT_OK=0
SCRIPT_ERROR=1
PEEBLE_CMD=$GOPATH/bin/pebble
PEEBLE_SERVICE_URL="https://localhost:14000"

OK_STRING="[ \033[32mOK\033[37m ]"

# contains(string, substring)
#
# Returns 0 if the specified string contains the specified substring,
# otherwise returns 1.
contains() {
    string=i"$1"
    substring="$2"
    if test "${string#*$substring}" != "$string"
    then
        return 0    # $substring is in $string
    else
        return 1    # $substring is not in $string
    fi
}

send_error(){
    error=$1
    cat << EOF >&2
$error
EOF
    exit $SCRIPT_ERROR
}

is_running() {
    for out in $(ps aux | grep $2 | $AWK_CMD '{print $11";"$2}')
    do
        PROC=$(echo $out | sed -e "s/;/ /g" | $AWK_CMD '{print $1}')
        if contains $PROC "pebble"; then
           return 0
        fi
    done
    return 1
}

start_pebble(){
    echo "*************************************************************************************************"
    echo "* Candango automatoes Pebble Server Start Process"
    echo "* Config File: $2"
    echo "*"
    echo -n "* Starting Pebble Server "
    nohup $PEEBLE_CMD -config $2 > /dev/null 2>&1 &
    RETVAL=$(curl --cacert "$SCRIPT_PATH/../tests/certs/candango.minica.pem" --write-out %{http_code} --silent --output /dev/null "$PEEBLE_SERVICE_URL/dir" | tr -d ' ')
    while [ $RETVAL -ne 200 ]
    do
        sleep 1
        echo -n "."
        RETVAL=$(curl --cacert "$SCRIPT_PATH/../tests/certs/candango.minica.pem" --write-out %{http_code} --silent --output /dev/null "$PEEBLE_SERVICE_URL/dir" | tr -d ' ')
    done
    echo -e " $OK_STRING"
    echo "*************************************************************************************************"
    return 0
}

stop_pebble(){
    echo "*************************************************************************************************"
    echo "* Candango automatoes Pebble Server Start Process"
    echo "* Config File: $2"
    echo "*"
    echo -n "* Stopping Pebble Pebble Server "
    for out in $(ps aux | grep  $2 | $AWK_CMD '{print $11";"$2}')
    do
        PROC=$(echo $out | sed -e "s/;/ /g" | $AWK_CMD '{print $1}')
        if contains $PROC "pebble"; then
           PID=$(echo $out | sed -e "s/;/ /g" | $AWK_CMD '{print $2}')
           kill -9 $PID
           echo -e " $OK_STRING"
           echo "*************************************************************************************************"
           return 0
        fi
    done
    return 1
}

pebble_option_list() {
    case "$1" in 
        start)
            if is_running $@; then
                send_error "Peeble Server $2 is still running..."
            else
                start_pebble $@
            fi
            ;;
        stop)
            if is_running $@; then
                stop_pebble $@
            else
                send_error "Peeble Server $2 is not running..."
            fi
            ;;
        status)
            if is_running $@; then
                echo "Peeble Server $2 is running..."
            else
                echo "Peeble Server $2 is not running..."
            fi
            ;;
        *)
            send_error "Usage: $SCRIPT_NAME FILE_NAME {start|stop|status}"
            ;;
    esac
}

pebble_option_list $@
