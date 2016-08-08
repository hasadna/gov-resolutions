# -*- coding: utf-8 -*-

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'govsearch (+http://hasadna.org.il)'

# Obey robots.txt rules
# ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'scraper.pipelines.ResolutionPipeline': 300,
}

# auto throttling doesn't appear to be working right atm
# AUTOTHROTTLE_ENABLED = True
# AUTOTHROTTLE_DEBUG = True
# CONCURRENT_REQUESTS = 16
# CONCURRENT_REQUESTS_PER_DOMAIN = 8
# DOWNLOAD_DELAY = 0.25 # sec
# AUTOTHROTTLE_START_DELAY = 5.0
# AUTOTHROTTLE_MAX_DELAY = 60.0
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# RETRY_TIMES = 5

# Enable and configure HTTP caching (disabled by default)
# HTTPCACHE_ENABLED = True

# LOG_ENABLED = False
LOG_LEVEL = 'INFO'
