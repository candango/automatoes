#!/bin/bash
SCRIPT_PATH="`dirname \"$0\"`"
cd $SCRIPT_PATH
pwd
$GOPATH/bin/pebble -config "../tests/conf/pebble-config.json"
