#!/bin/bash
cd /home/omar/whatssapp/wisp-management-bot
/usr/bin/python3 /home/omar/whatssapp/wisp-management-bot/arp_extractor.py 192.168.26.1 mikrotik >> /home/omar/whatssapp/wisp-management-bot/logs/arp_extractor.log 2>&1
