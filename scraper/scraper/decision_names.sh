#!/bin/sh
cat dump.json | jq -Cr .url | xargs -I {} basename {} .aspx | sort
