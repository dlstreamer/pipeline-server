#!/bin/bash -e
ERRCODE=0
echo "Starting container..."
command1='echo "starting Video Analytics Serving"; cd app/server; python3 -m openapi_server $@ &'
command2='echo "starting your executable"; cd ../..; ./<your_application_executable> &'

commands=(
    "{ $command1 }"
    "{ $command2 }"
)
numcmds=`expr "${#commands[@]}" - 1`
for i in `seq 0 "$numcmds"`; do
    echo "Launching Command# $i in background..."
    eval "${commands[$i]} ;"
    echo "Command# ${i} running as PID# ${!}"
done

# await exit from any launched process
wait -n

ERRCODE=$?
echo $ERRCODE
if [ "$ERRCODE" == "0" ];
then
echo "Closed Container Successfully"
else
echo "Fatal Exit! ($ERRCODE)"
fi
# signal all members in this process group
kill 0
