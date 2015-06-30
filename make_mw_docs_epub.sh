#!/usr/bin/env bash


active_server=0


listening_server=$(netstat -tan | grep LISTEN | grep 5070)
if [[ -z "$command" ]]; then {
    python runserver.py &
    server_ppid=$!
    active_server=1
}; fi


## Start a server if not already running
#n_running_servers=$(pgrep -fc 'python runserver.py')
#if [ "$n_running_servers" == 0 ]; then {
#    python runserver.py &
#    server_ppid=$!
#}; fi

pushd dispatcher

# Cleanup and prepare directories.
rm -rf docs/dispatcher.*
rm -rf docs/build
rm -rf static/docs
mkdir -p static

# Build rst
sphinx-apidoc -F -o docs .


# Build docs
# sphinx-build -b html -d docs/build/doctrees docs static/docs
sphinx-build -b epub -d docs/build/doctrees docs static/docs
# sphinx-build -b singlehtml -d docs/build/doctrees docs static/docs

# Kill server if we started it.
#if [ "$n_running_servers" == 0 ]; then pkill -P $server_ppid; fi
if [[ "$active_server" == 1 ]]; then pkill -P $server_ppid; fi

popd


# epydoc --html dispatcher --graph all -o ddd 

