* Steps 1 and 2 are not shown, only one instance running

* Step 3, a new instance starts. This triggers the cpuhigh ALARM on the base instance (i-204b836a). The autoscaler starts a new instance.
```
2013-02-04 23:54 [MainProcess]	"GET /ping HTTP/1.0" 200 -
2013-02-04 23:58 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 23:58 [MainProcess]	Notification for cpuhigh ALARM on instance i-204b836a
2013-02-04 23:58 [MainProcess]	Trying to start instance i-68ce1f22
2013-02-04 23:58 [MainProcess]	Adding instance i-68ce1f22 to load balancer
2013-02-04 23:58 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-04 23:59 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-04 23:59 [MainProcess]	Notification for cpulow ALARM on instance i-204b836a
2013-02-04 23:59 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:02 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Step 4, client D starts, and the second instance also issues an cpuhigh alarm. 
```
2013-02-05 00:02 [MainProcess]	Notification for cpuhigh ALARM on instance i-68ce1f22
2013-02-05 00:02 [MainProcess]	No instance available to start
2013-02-05 00:02 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:02 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-05 00:02 [MainProcess]	Notification for cpulow ALARM on instance i-68ce1f22
2013-02-05 00:02 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:18 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Steps 5, 6, 7 cause the cpu load to drop. The fact is noted but no action is taken yet because of the 5-minute and average time-lag, which causes the values to drop rather slow.
```
2013-02-05 00:18 [MainProcess]	Notification for cpuhigh OK on instance i-204b836a
2013-02-05 00:18 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:22 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-05 00:22 [MainProcess]	Notification for cpuhigh OK on instance i-68ce1f22
2013-02-05 00:22 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:24 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Step 8, client C stops. The autoscaler removes the second instance.
```
2013-02-05 00:24 [MainProcess]	Notification for cpulow OK on instance i-204b836a
2013-02-05 00:24 [MainProcess]	Not scaling down instance i-204b836a which is the base
2013-02-05 00:24 [MainProcess]	Not scaling down instance i-204b836a which is the base
2013-02-05 00:24 [MainProcess]	Removing instance i-68ce1f22 form load balancer
2013-02-05 00:24 [MainProcess]	Stopping instance i-68ce1f22
2013-02-05 00:24 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:28 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Step 9, and an accidental login to the server and tail -f on log files causes another cpuhigh alert
```
2013-02-05 00:28 [MainProcess]	Notification for cpuhigh ALARM on instance i-204b836a
2013-02-05 00:28 [MainProcess]	Trying to start instance i-68ce1f22
2013-02-05 00:28 [MainProcess]	Adding instance i-68ce1f22 to load balancer
2013-02-05 00:28 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:29 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* logging out solved the problem, the cpulow is triggered and the second instance is stopped again.
```
2013-02-05 00:29 [MainProcess]	Notification for cpulow ALARM on instance i-204b836a
2013-02-05 00:29 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:31 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-05 00:31 [MainProcess]	Notification for cpulow OK on instance i-68ce1f22
2013-02-05 00:31 [MainProcess]	Removing instance i-68ce1f22 form load balancer
2013-02-05 00:31 [MainProcess]	Stopping instance i-68ce1f22
2013-02-05 00:31 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:32 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
2013-02-05 00:32 [MainProcess]	Notification for cpuhigh OK on instance i-204b836a
2013-02-05 00:32 [MainProcess]	"POST / HTTP/1.0" 200 -
2013-02-05 00:34 [MainProcess]	Received notification for topic arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop
```

* Finally, the first instance also is low and thus finishes it by terminating the secondary instance.
```
2013-02-05 00:34 [MainProcess]	Notification for cpulow OK on instance i-204b836a
2013-02-05 00:34 [MainProcess]	Not scaling down instance i-204b836a which is the base
2013-02-05 00:34 [MainProcess]	Not scaling down instance i-204b836a which is the base
2013-02-05 00:34 [MainProcess]	No running instance to scale down. Hence terminating all stopped.
2013-02-05 00:34 [MainProcess]	"POST / HTTP/1.0" 200 -
```