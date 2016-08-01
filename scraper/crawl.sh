#!/bin/sh
set -ex
for i in `seq 0 6`; do scrapy crawl resolutions -a gov_index=$i; done 
