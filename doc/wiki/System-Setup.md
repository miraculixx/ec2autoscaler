EC2 instances
-------------
Every EC2 instance is setup is as follows:

* nginx
  * installed as default by apt-get
  * configured using this [configuration](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/config/nginx-proxy-conf)
  * proxies two ports, 10000 to 10001 for the autoscaler, 30000 to 30001 for the worker

* /etc/init.d
  * kasworker - starts, stops the worker process
  * autoscaler - starts, stops the autoscaler

* /opt/kooaba-worker (linked to /opt/OhHo4oop-ec2autoscale)
  * contains all scripts, configuration files etc.
  * is a git pull from [this](https://github.com/miraculixx/OhHo4oop-ec2autoscale) repository, which is just a very cheap approach to deploy the software to the server 
  * home also contains a ./kooaba-worker. To get started, after logging in just
```
cd kooaba-worker
scripts/admin.sh -h
```

* within /opt/kooaba-worker
  * config - contains all config files. Important are ec2rc and setenv. These set various config variables that determine defaults for EC2 and the admin scripts, autoscaler etc.
  * scripts - convenience scripts
  * doc - some documentation files, most of it is in this wiki though
  * src - the python source code
  * puppet - abonndened approach to automate server setup
  * test - an approach to unit testing, far from complete... 

Load Balancer
-------------
The ELB is currently configured as follows (instance ids may change). Note that in the scaled-down state only the base instance (i-204b836a) is registered with the ELB.
```
$ scripts/admin.sh -b | grep OhHo4oop
  OhHo4oop       OhHo4oop-1996069.eu-west-1.elb.amazonaws.com                      
  OhHo4oop       OhHo4oop-1996069.eu-west-1.elb.amazonaws.com i-24d7066e    unknown
  OhHo4oop       OhHo4oop-1996069.eu-west-1.elb.amazonaws.com i-204b836a    unknown
```

Alarms
------
CloudWatch has the following alarms defined:
```
$ scripts/admin.sh -w | grep OhHo4oop
       instance         OhHo4oop:cpuhigh:i-204b836a  CPUUtilization(Average)>=75.0    300      i-204b836a             autoscale-OhHo4oop
       instance         OhHo4oop:cpuhigh:i-24d7066e  CPUUtilization(Average)>=85.0    300      i-24d7066e             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-204b836a  CPUUtilization(Average)>=58.0    300      i-204b836a             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-24d7066e  CPUUtilization(Average)>=45.0    300      i-24d7066e             autoscale-OhHo4oop

```

EC2 instances
-------------
The following instances are defined (m1.small type, based on AMI ami-c1aaabb5, Ubuntu Linux 12.04 Server)
```
$ scripts/admin.sh -l
(filtered for instances with key=OhHo4oop)
        id   key_name      state                                    public_dns_name                 name
i-204b836a   OhHo4oop    running  ec2-54-228-18-168.eu-west-1.compute.amazonaws.com        OhHo4oop_base
i-24d7066e   OhHo4oop    running  ec2-54-246-54-238.eu-west-1.compute.amazonaws.com  OhHo4oop-i-24d7066e
```

SNS 
---
* Topic: arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
* HTTP (for POST): http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:10000
* Ping: http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:10000/ping
