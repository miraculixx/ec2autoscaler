Here is a sample run of the real-scase scenario, as provided in the email. The autoscaler log is split into several parts and annotated to explain what is going on. While the scneario is not yet exactly followed, the run nevertheless demonstrates that autoscaling works.

* Step 1 - the test started at 11:24, and was set up to run for one hour in total (to make sure at least one client, A, runs for the full time). At 11:24 the autoscaler received a cpulow ALARM for instance i-204b836a, which is the base load instance and also runs the autoscaler. The alarm shows that client A started its work.
```
2013-02-04 11:24 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 11:24 [MainProcess]	Notification for cpulow ALARM on instance i-204b836a
2013-02-04 11:24 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-04 11:33 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Step 2 - client B starts, and generates a cpuhigh ALARM. This is too early, so we will have to adjust the threshold. It would also be nice to include the actual measurement value in the alarm to have a reference. A new instance is added.
```
2013-02-04 11:33 [MainProcess]	Notification for cpuhigh ALARM on instance i-204b836a
2013-02-04 11:33 [MainProcess]	Trying to start instance i-1e06d154
2013-02-04 11:33 [MainProcess]	Adding instance i-1e06d154 to load balancer
2013-02-04 11:33 [MainProcess]	"POST / HTTP/1.0" 200 -
```

* Step 2b - we can see the effect of the new instance on the base instance, its cpuhigh ALARM goes back within 5 minutes of adding a new instance. 
```
2013-02-04 11:38 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 11:38 [MainProcess]	Notification for cpuhigh OK on instance i-204b836a
2013-02-04 11:38 [MainProcess]	"POST / HTTP/1.0" 200 -
```

* Step 3 - client C starts, and we can see growing load on i-1e06d154 (cpulow ALARM), the second instance now running. Because its alarm threshold for cpuhigh is higher than for the base instance (85% instead of 65%), this alarm is not triggered.
```
2013-02-04 11:40 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 11:40 [MainProcess]	Notification for cpuhigh OK on instance i-1e06d154
2013-02-04 11:40 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-04 11:40 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 11:40 [MainProcess]	Notification for cpulow ALARM on instance i-1e06d154
2013-02-04 11:40 [MainProcess]	"POST / HTTP/1.0" 200 -
```
* Steps 4 to 7. Client D starts processing, but client B stops. So there are now 4, 3 and 2 clients running. Because of load balancing both instances show at least 30% of CPU load and hence will not shut down. There is no log data for these steps because there were no triggers.

* Steps 8 and 9. Clients C and A also stop, and trigger the cpulow OK notifications on both instances. The base instance is programmed not to shut down. The second instance is stopped and removed from the load balancer.   
```
2013-02-04 12:24 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 12:24 [MainProcess]	Notification for cpulow OK on instance i-204b836a
2013-02-04 12:24 [MainProcess]	Not scaling down instance i-204b836a which is the base
2013-02-04 12:24 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-04 12:25 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 12:25 [MainProcess]	Notification for cpulow OK on instance i-1e06d154
2013-02-04 12:25 [MainProcess]	Removing instance i-1e06d154 form load balancer
2013-02-04 12:25 [MainProcess]	Stopping instance i-1e06d154
2013-02-04 12:25 [MainProcess]	"POST / HTTP/1.0" 200 -
```

* Alarm settings were as follows (only type=instance is relevant):
```
$ scripts/admin.sh -w
           type                                name                         metric period       dimension                   topic(short)
   loadbalancer                    HighRequestCount      RequestCount(Average)>2.0     60        Iji4xohf             autoscale-Iji4xohf
      autoscale                    KaseHighCPUAlarm  CPUUtilization(Average)>=35.0     60    asg-Beecae8U      policyName/sp-UP-Beecae8U
      autoscale                     KaseLowCPUAlarm  CPUUtilization(Average)<=35.0     60    asg-Beecae8U    policyName/sp-DOWN-Beecae8U
       instance         OhHo4oop:cpuhigh:i-1e06d154  CPUUtilization(Average)>=85.0    300      i-1e06d154             autoscale-OhHo4oop
       instance         OhHo4oop:cpuhigh:i-204b836a  CPUUtilization(Average)>=65.0    300      i-204b836a             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-1e06d154  CPUUtilization(Average)>=20.0    300      i-1e06d154             autoscale-OhHo4oop
       instance          OhHo4oop:cpulow:i-204b836a  CPUUtilization(Average)>=20.0    300      i-204b836a             autoscale-OhHo4oop
```