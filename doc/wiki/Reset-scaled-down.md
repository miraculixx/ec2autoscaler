To reset to a scaled-down state, first make sure there is at least one stopped instance:
```
$ cd kooaba-worker
$ scripts/admin.sh -l
```

If there is none, create a new one. This will create a new instance and run it. The -p and -t options define alarms for the new instance (cpulow>=45/high>=85, for 300 seconds intervals). 
```
$ scripts/admin.sh -a -m -p 300 -t 45:85
```

Then bootstrap the new instance by getting its public dns name from the admin.sh -l command and passing that as a parameter to the bootstrap script:
```
$ scripts/admin.sh -l
        id   key_name      state                                    public_dns_name                 name
i-204b836a   OhHo4oop    running  ec2-54-228-18-168.eu-west-1.compute.amazonaws.com        OhHo4oop_base
i-68ce1f22   OhHo4oop    running   ec2-54-247-14-23.eu-west-1.compute.amazonaws.com  OhHo4oop-i-68ce1f22
$ scripts/bootstrap.sh ec2-54-247-14-23.eu-west-1.compute.amazonaws.com
```

This will transfer and run scripts/setup.sh on this instances, taking 1-2 minutes. After that you should stop the new instance:
```
$ scripts/admin.sh -s -i i-123456
```

**Note that the autoscaler code could easily be extended to do all of this, that is create new instances on the fly when needed, rather than to rely on a manual process.**
