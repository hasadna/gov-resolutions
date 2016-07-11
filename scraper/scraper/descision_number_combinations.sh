#!/bin/sh

cat $1 \
    | jq -Cr .url \
    | xargs -I {} basename {} .aspx \
    | sed 's/[0-9]/\./g' \
    | sort \
    | uniq
