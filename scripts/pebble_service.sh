#!/bin/bash
##
## Copyright 2019-2023 Flavio Gonçalves Garcia
## Copyright 2020 Viktor Szépe
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
##
## Author: Flavio Garcia <piraz@candango.org>

AWK_CMD="/usr/bin/awk"
PWD_PATH="/usr/bin/pwd"

SCRIPT_PATH=$(dirname "$0")
SCRIPT_NAME=$(basename "$0")

SCRIPT_OK=0
SCRIPT_ERROR=1
GOPATH=${GOPATH:-$HOME/go}
PEBBLE_CMD=$GOPATH/bin/pebble
PEBBLE_SERVICE_URL="https://localhost:14000"
PEBBLE_LOG_FILE="/tmp/automatoes-pebble.log"
PEBBLE_START_TIMEOUT=${PEBBLE_START_TIMEOUT:-30}
PEBBLE_CERT_PATH="$SCRIPT_PATH/../tests/certs/localhost/cert.pem"
PEBBLE_CA_CERT_PATH="$SCRIPT_PATH/../tests/certs/candango.minica.pem"
PEBBLE_CA_KEY_PATH="$SCRIPT_PATH/../tests/certs/candango.minica.key.pem"

OK_STRING="[ \033[32mOK\033[37m ]"

# contains(string, substring)
#
# Returns 0 if the specified string contains the specified substring,
# otherwise returns 1.
contains()
{
    local string=i"$1"
    local substring="$2"

    # Whether $substring is in $string
    test "${string#*$substring}" != "$string"
}

send_error()
{
    local error="$1"
    cat <<EOF >&2
$error
EOF

    exit $SCRIPT_ERROR
}

renew_pebble_certificate_if_needed()
{
    if [ -f "$PEBBLE_CERT_PATH" ] && \
       openssl x509 -checkend 86400 -noout \
           -in "$PEBBLE_CERT_PATH" >/dev/null 2>&1
    then
        return $SCRIPT_OK
    fi

    if [ ! -x "$GOPATH/bin/minica" ]; then
        send_error "minica not found at $GOPATH/bin/minica. Run scripts/install_pebble.sh."
    fi

    echo "* Renewing Pebble localhost certificate"
    rm -rf "$SCRIPT_PATH/../tests/certs/localhost"
    (
        cd "$SCRIPT_PATH/../tests/certs" || exit $SCRIPT_ERROR
        "$GOPATH/bin/minica" \
            -domains localhost \
            -ca-cert "$(basename "$PEBBLE_CA_CERT_PATH")" \
            -ca-key "$(basename "$PEBBLE_CA_KEY_PATH")"
    ) || return $SCRIPT_ERROR
}

is_running()
{
    for out in $(ps aux | grep "$2" | $AWK_CMD '{print $11";"$2}')
    do
        PROC=$(echo $out | sed -e "s/;/ /g" | $AWK_CMD '{print $1}')
        if contains "$PROC" "pebble"; then
           return 0
        fi
    done

    return $SCRIPT_ERROR
}

start_pebble()
{
    renew_pebble_certificate_if_needed || return $SCRIPT_ERROR

    export PEBBLE_AUTHZREUSE=0
    export PEBBLE_WFE_NONCEREJECT=0
    export PEBBLE_VA_ALWAYS_VALID=1
    export PEBBLE_VA_NOSLEEP=1

    echo "*************************************************************************************************"
    echo "* Candango automatoes Pebble Server Start Process"
    echo "* Config File: $2"
    echo "*"
    echo "* Log File: $PEBBLE_LOG_FILE"
    echo -n "* Starting Pebble Server "
    nohup "$PEBBLE_CMD" -strict=false -config "$2" >"$PEBBLE_LOG_FILE" 2>&1 &
    RETVAL=$(curl --cacert "$PEBBLE_CA_CERT_PATH" --write-out %{http_code} --silent --output /dev/null "$PEBBLE_SERVICE_URL/dir" | tr -d ' ')
    WAITED=0
    while [ "$RETVAL" -ne 200 ]
    do
        if [ "$WAITED" -ge "$PEBBLE_START_TIMEOUT" ]; then
            echo ""
            echo "* Pebble failed to start after $PEBBLE_START_TIMEOUT seconds."
            echo "* Last Pebble log output:"
            tail -50 "$PEBBLE_LOG_FILE" >&2
            return $SCRIPT_ERROR
        fi
        sleep 1
        WAITED=$((WAITED + 1))
        echo -n "."
        RETVAL=$(curl --cacert "$PEBBLE_CA_CERT_PATH" --write-out %{http_code} --silent --output /dev/null "$PEBBLE_SERVICE_URL/dir" | tr -d ' ')
    done
    echo -e " $OK_STRING"
    echo "*************************************************************************************************"

    return $SCRIPT_OK
}

stop_pebble()
{
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
           return $SCRIPT_OK
        fi
    done

    return $SCRIPT_ERROR
}

pebble_option_list()
{
    case "$1" in 
        start)
            if is_running "$@"; then
                send_error "Peeble Server $2 is still running..."
            else
                start_pebble "$@"
            fi
            ;;
        stop)
            if is_running "$@"; then
                stop_pebble "$@"
            else
                send_error "Peeble Server $2 is not running..."
            fi
            ;;
        status)
            if is_running "$@"; then
                echo "Peeble Server $2 is running..."
            else
                echo "Peeble Server $2 is not running..."
            fi
            ;;
        *)
            send_error "Usage: $SCRIPT_NAME {start|stop|status} FILE_NAME"
            ;;
    esac
}

pebble_option_list "$@"
