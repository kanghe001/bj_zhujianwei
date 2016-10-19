#!/usr/bin/env python
# coding=utf8

f1 = file('/home/kanghe/bjzjw_url.txt', 'r')
li = f1.readlines()
f2 = file('/home/kanghe/all_url.txt', 'w')
for line in li:
    f2.write('' + line.strip('\r\n') + '\n')
f1.close()
f2.close()

