The first setup of the EC2 instance was done manually, but obviously that is not a sustainable
approach for a prouction environment. It takes too long to set up a new instance and it is error
prone. So we will want to automate this.  

* To this end, wrote an [admin utility](https://github.com/miraculixx/OhHo4oop-ec2autoscale/blob/master/src/client/admin.py). With this, creating a new instance is a single command:
```
$ python src/client/admin.py -a 
Creating EC2 Connection
Creating instance
Created instance i-24be746e
```

* The details of the new instance are easily retrieved by another command:
```
$ python src/client/admin.py -l 
        id   key_name      state                                    public_dns_name
i-f28346b8   Iji4xohf    stopped                                                   
i-24be746e   OhHo4oop    pending    ec2-54-228-5-40.eu-west-1.compute.amazonaws.com
i-56726a1f       eval    running  ec2-54-247-160-17.eu-west-1.compute.amazonaws.com
i-76e92d3c   Iji4xohf    stopped                                                   
i-204b836a   OhHo4oop    running  ec2-54-228-37-115.eu-west-1.compute.amazonaws.com
i-fed413b4   Iji4xohf    stopped                                                   
i-75b1413d       eval    running  ec2-46-137-63-234.eu-west-1.compute.amazonaws.com
```

* Once the instance is in running state, it can be bootstrapped (install all software required)
by the following command. This will automatically copy setup.sh and execute it. setup.sh issues the appropriate apt-get commands and gets our server's code from github. It also sets up the nginx proxy accordingly and restarts nginx.
```
$ scripts/bootstrap.sh  ec2-54-228-5-40.eu-west-1.compute.amazonaws.com
```
* We can also use an arbitrary machine to run the autoscaler (my implementation) by giving the
autoscaler parameter. This will use /etc/init.d/autoscaler to start the autoscaler service.
```
$ scripts/bootstrap.sh  ec2-54-228-5-40.eu-west-1.compute.amazonaws.com autoscaler
```

* To see if services are running, the admin script provides a ping command:
```
$ scripts/admin.sh --ping -i i-204b836a
Worker-Ping at http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:30000/ping
OK
Scaler-Ping at http://ec2-54-228-18-168.eu-west-1.compute.amazonaws.com:10000/ping
OK
```

* Further we can test the autoscaler by either running the scale up/down policies directly, or by using the alert mechanism of CloudWatch:
```
# select the first stopped instance and start it, register in load balancer
$ scripts/admin.sh --scale-up
# select the first non _base instance and stop it, de-register from load balancer
$ scripts/admin.sh --scale-down
```

* Retrieving a list of defined alarms in CloudWatch:
```
$ scripts/admin.sh --list-alarms
           type                                name                         metric period       dimension                   topic(short)
   loadbalancer                    HighRequestCount      RequestCount(Average)>2.0     60        Iji4xohf             autoscale-Iji4xohf
      autoscale                    KaseHighCPUAlarm  CPUUtilization(Average)>=35.0     60    asg-Beecae8U      policyName/sp-UP-Beecae8U
      autoscale                     KaseLowCPUAlarm  CPUUtilization(Average)<=35.0     60    asg-Beecae8U    policyName/sp-DOWN-Beecae8U
       instance         OhHo4oop:cpuhigh:i-1e06d154  CPUUtilization(Average)>=65.0    300      i-1e06d154             autoscale-OhHo4oop
       instance         OhHo4oop:cpuhigh:i-204b836a  CPUUtilization(Average)>=65.0    300      i-204b836a             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-1e06d154  CPUUtilization(Average)>=20.0    300      i-1e06d154             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-204b836a  CPUUtilization(Average)>=20.0    300      i-204b836a             autoscale-OhHo4oop
```

* Define alarm settings
```
# define cpulow at 35.0, cpuhigh at 85. All alarms are defined >=
$ scripts/admin.sh -m -i i-1e06d154 -t 35:85
```