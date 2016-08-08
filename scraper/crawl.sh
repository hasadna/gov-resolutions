#!/bin/sh
set -ex
scrapy crawl resolutions -a gov_indexes=0,1,2,3,4,5,6
