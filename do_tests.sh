#!/bin/bash

# This runs performance tests on the program.

#these are the commands to run.

#if these variables are anything but "true", they don't get done
DO_TIMING=true
DO_MEM_USAGE=false

#this is applied to all commands, for both timing or memory
TIMING_GLOBAL_ARGS=-st
MEM_USAGE_GLOBAL_ARGS=

TESTS=(
    'python interpreter.py -i input -m 5 -p -x enterprise'
    'python interpreter.py -i input -m 5 -p -x fractal_tree'
    'python interpreter.py -i input2 -m 5 -p -x space_station -a'
    'python interpreter.py -i input2 -m 5 -p -x spike_ship -a'
    'python interpreter.py -i input2 -m 5 -p -x wing_ship -a'
    'python interpreter.py -i input2 -m 5 -p -x c_station -a'
    'python interpreter.py -i input2 -m 5 -p -x rotational_ship -a'
    'python interpreter.py -i input2 -m 5 -p -x tie_fighter -a'
)

echo "================================================================================================="

#this runs the commands and redirects all their output to a file with the same name as the command.
count=0
while [ "x${TESTS[count]}" != "x" ]
do
    # list the command and time it started
    echo -e "\n**************************Running the following command: ${TESTS[count]}"
    echo "**************************at time:"
    date
    echo -e "\n\n"

    #run a timing test if so specified
    if [ ${DO_TIMING} == "true" ]
    then
	echo -e "******************************TIMING:\n\n"
        #run the command
	${TESTS[count]} ${TIMING_GLOBAL_ARGS}
    else
	echo "*****************************timing was not done"
    fi

    #run a memory usage test if so specified.
    if [ ${DO_MEM_USAGE} == "true" ]
    then
	echo -e "\n\n******************************MEMORY USAGE:\n\n"
        #run the command
	valgrind --tool=massif --massif-out-file=temp.massif --threshold=100.0 --depth=2 ${TESTS[count]} ${MEM_USAGE_GLOBAL_ARGS}
	ms_print temp.massif
	rm temp.massif
    else
	echo -e "\n\n*****************************memory usage was not done"
    fi

    #make a note of when it stopped
    echo -e "\n\n\n**************************the program finished at:"
    date
    echo -e "\n\n\n=================================================================================================\n\n"

    #increase the counter
    count=$(( $count + 1 ))
done