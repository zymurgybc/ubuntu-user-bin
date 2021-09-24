#!/usr/bin/bash

# https://serverfault.com/questions/151109/how-do-i-get-the-current-unix-time-in-milliseconds-in-bash
echo "a) " $(date +%s%N) " (epoch milliseconds)"

echo "b) " $(echo "obase=16; $(date +%s%N)" | bc) "    (epoch milliseconds as MSB-LSB bytes)"

echo "c) " $(echo "obase=16; $(date +%s%N)" | bc | fold -w2 | tac | tr -d "\n" ; echo "" )  "    (epoch milliseconds as LSB-MSB bytes)"

# https://unix.stackexchange.com/questions/191205/bash-base-conversion-from-decimal-to-hex
#echo $(([##16]dec))
#echo $(([##16]`date +%s%N`))
