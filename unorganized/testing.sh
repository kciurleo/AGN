#!/bin/sh

cd "/opt/pwdata/katie/csc2.1data"
list1=(*)

cd "/opt/pwdata/katie/csc2.1"
list2=(*)

echo "Files in 2.1data but not 2.1"
comm -23 <(printf "%s\n" "${list1[@]}" | sort) <(printf "%s\n" "${list2[@]}" | sort)
echo

echo ${#list1[@]}

echo ${#list2[@]}