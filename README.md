# irc_robot Handbook

> IRC robot named **redbot-rt** in `#rt-qe` channel, to provide the query of kernel-rt version and kernel bug in IRC.

## Environment
This script was written by python2.x, using socket tech (similar to Apache Kafka in some parts in my opinion) on IRC chat tool (a chat tool in Linux platform), the purpose is to get rid of querying various kernel-rt nvr troubles.

## Introduction
There are the following function:
* The response nvr of kernel-rt are based on brew platform.
* The robot can return the latest nvr of kernel-rt, especially, if you type in a specific normal YStream kernel you will get the latest nvr related this kernel.

## Usage
> Wake it by type in nvr with prefix ”:“.

For example:

```
[10:30:37] 20<yonwang>30 :rhel7
[10:30:57] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-3.10.0-983.rt56.937.el7
[10:30:58] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-3.10.0-957.5.1.rt56.916.el7
[10:31:00] 20<yonwang>30 :rhel8
[10:31:09] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-4.18.0-9.rt5.41.el8
[10:31:10] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-4.18.0-0.rc8.4.rt0.23.el8
[10:31:34] 20<yonwang>30 :kernel-3.10.0-957.el8
[10:31:57] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-3.10.0-957.rt56.910.el7
[10:31:58] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-3.10.0-957.5.1.rt56.916.el7
[10:32:02] 20<yonwang>30 :RHEL-8.0-20181218.0
[10:32:19] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-4.18.0-9.rt5.41.el8
[10:32:19] 19<redbot-rt> yonwang: Latest RT brew build: kernel-rt-4.18.0-0.rc8.4.rt0.23.el8
```
