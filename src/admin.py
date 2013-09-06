# AutoScaler for Amazon AWS
# (c) 2013 Patrick Senti
# patrick dot senti at gmx dot net
#
# Usage:
# use admin.py -h to get help
#

import scaler
import boto.ec2.cloudwatch.alarm
#! /usr/bin/python

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="patrick"
__date__ ="$Feb 1, 2013 7:49:01 PM$"

from optparse import OptionParser
from workermgr import *
from scaler import *

import os
import sys
import codecs
import urllib2

class DummyInstance:
    def __init__(self):
        inst = self
        inst.id = "some-id"
        inst.public_dns_name = "some.dns.name"
        inst.state="undefined"
        inst.key_name="some-key"


def init():
    parser = OptionParser()
    parser.add_option("-a", "--add-instance",
                      help="add instance",
                      action="store_true",
                      dest="add",
                      default=False)
    parser.add_option("-T", "--terminate-instance",
                      help="terminate instance with ID",
                      action="store_true",
                      dest="terminate",
                      default=False)
    parser.add_option("-d", "--dry",
                      help="no action, just dry run",
                      action="store_true",
                      dest="dryrun",
                      default=False)
    parser.add_option("-i", "--instance-id",
                      help="instance ID",
                      action="store",
                      dest="id",
                      default=None)
    parser.add_option("-l", "--list",
                      help="list instances",
                      action="store_true",
                      dest="list",
                      default=False)
    parser.add_option("-r", "--run",
                      help="start instance ID",
                      action="store_true",
                      dest="start",
                      default=False)
    parser.add_option("-s", "--stop",
                      help="stop instance ID",
                      action="store_true",
                      dest="stop",
                      default=False)
    parser.add_option("-g", "--get-tags",
                      help="get tags of an instance",
                      action="store_true",
                      dest="tags",
                      default=False)
    parser.add_option("-w", "--list-alarms",
                      help="list CloudWatch alarms",
                      action="store_true",
                      dest="listalarms",
                      default=False)
    parser.add_option("-S", "--start-autoscaler",
                      help="start autoscaler on instance ID",
                      action="store_true",
                      dest="autoscaler",
                      default=False)
    parser.add_option("-m", "--monitor-instance",
                      help="add a CloudWatch CPU monitor to instance ID or loadbalancer NAME",
                      action="store_true",
                      dest="monitor",
                      default=False)
    parser.add_option("-b", "--list-elb",
                      help="list loadbalancers",
                      action="store_true",
                      dest="listlb",
                      default=False)
    parser.add_option("-n", "--loadbalancer",
                      help="loadbalancer name",
                      action="store",
                      dest="lbname",
                      default=None)
    parser.add_option("-t", "--threshold",
                      help="alarm threshold in CPU percent (LOW:HIGH) or request count (loadbalancer)",
                      action="store",
                      dest="thres",
                      default=None)
    parser.add_option("-p", "--period",
                      help="measurement periods in seconds (defaults to 300)",
                      action="store",
                      dest="period",
                      default=300)
    parser.add_option("", "--test-alarm",
                      help="set alarm state for test purposes (name/state, where state is OK, ALARM, INSUFFICIENT_DATA)",
                      action="store",
                      dest="alarm_state",
                      default=None)
    parser.add_option("-o", "--log",
                      help="set log file name",
                      action="store",
                      dest="logfile",
                      default=None)
    parser.add_option("", "--pidfile",
                      help="set pid file for autoscaler",
                      action="store",
                      dest="pidfile",
                      default="/var/run/autoscaler.pid")
    parser.add_option("", "--ping",
                      help="ping instance ID",
                      action="store_true",
                      dest="ping",
                      default=False)
    parser.add_option("", "--scale-up",
                      help="start the first stopped instance and add to load balancer",
                      action="store_true",
                      dest="scaleup",
                      default=False)
    parser.add_option("", "--scale-down",
                      help="stop the first running instance (except _base) and remove from load balancer",
                      action="store_true",
                      dest="scaledown",
                      default=False)
    return parser


parser = init()
(opt, args) = parser.parse_args()

sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
if opt.logfile:
    f = open(opt.logfile, "w")
    sys.stderr = f

# set default instance helper
mgr = KooabaWorkerManager()

if opt.dryrun:
    # this is to allow for try runs
    mgr=KooabaWorkerManagerDryRun()
    print "*** Dry run ***"
    
if opt.add:
    inst = mgr.create_instance()
    print "Created instance %s" % inst.id
    opt.id = inst.id

if opt.terminate:
    if opt.id != None:
        mgr.terminate_instance(opt.id)
        print "Terminated instance %s" % opt.id
        scaler = AutoScaler()
        scaler.remove_monitor_instance(opt.id)
        print "Removed instance %s from CloudWatch" % opt.id
        if opt.lbname != None:
            elb = scaler.connect_elb()
            elb.deregister_instances(opt.lbname, [opt.id])
            print "Removed instance %s from loadbalancer %s" % (opt.id, opt.lbname)
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.start:
    if opt.id != None:
        inst = mgr.get_instance(opt.id)
        inst.start()
        print "Started instance %s" % opt.id
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.stop:
    if opt.id != None:
        inst = mgr.get_instance(opt.id)
        inst.stop()
        print "Stopped instance %s" % opt.id
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.tags:
    tags = mgr.get_tags()
    print "%10s %10s %10s" % ("id", "key", "value")
    for inst in tags:
        for key in tags[inst]:
            map = tags[inst]
            print "%10s %10s %-10s" % (inst, key, map[u'Name'])
    
if opt.list:
    filter = os.environ['KAS_KEYFILTER']
    # print list of instances
    list = mgr.get_instances(key_name=filter)
    if filter != '':
        print "(filtered for instances with key=%s)" % filter
    print "%10s %10s %10s %50s %20s" % ("id", "key_name", "state", "public_dns_name", "name")
    for id in list:
        inst = list[id]
        print "%10s %10s %10s %50s %20s" % (inst.id, inst.key_name, inst.state, inst.public_dns_name, inst.name)

if opt.listlb:
    # print list of load balancers
    scaler = AutoScaler()
    lblist = scaler.get_loadbalancers()
    print "%10s %50s %10s %10s" % ("name", "public_dns_name", "id", "state")
    for lb in lblist:
        print "%10s %50s %10s %10s" % (lb.name, lb.dns_name, '', '')
        try:
            health = lb.get_instance_health(lb.instances)
        except:
            health = None
        for inst in lb.instances:
            if health != None and inst.id in health:
                instinfo = health[inst.id]
                print "%10s %50s %10s %10s" % (lb.name, lb.dns_name, instinfo.instance_id, instinfo.state)
            else:
                print "%10s %50s %10s %10s" % (lb.name, lb.dns_name, inst.id, "unknown")

if opt.listalarms:
    scaler = AutoScaler()
    list = scaler.get_alarms()
    print "%15s %35s %30s %6s %15s %30s" % ("type", "name", "metric", "period", "dimension", "topic(short)")
    for alarm in list:
        metric = "%s(%s)%s%s" % (alarm.metric, alarm.statistic, alarm.comparison, alarm.threshold)
        # check type of alarm
        if u'InstanceId' in alarm.dimensions:
            type = 'instance'
            dimension = alarm.dimensions[u'InstanceId'][0]
        if u'LoadBalancerName' in alarm.dimensions:
            type = 'loadbalancer'
            dimension = alarm.dimensions[u'LoadBalancerName'][0]
        if u'AutoScalingGroupName' in alarm.dimensions:
            type = 'autoscale'
            dimension = alarm.dimensions[u'AutoScalingGroupName'][0]
        # the short name for the topic is the last item in the : separated string
        arn_topic = alarm.alarm_actions[0].split(":")[-1]
        print "%15s %35s %30s %6s %15s %30s" % (type,
                                       alarm.name,
                                       metric,
                                       alarm.period,
                                       dimension,
                                       arn_topic,
                                      )
                                      
if opt.autoscaler:
    if opt.id != None:
        moninst = mgr.get_instance(opt.id)
        print "AutoScaler starting"
        scaler = AutoScaler()
        scaler.set_url(moninst.public_dns_name)
        f = open(opt.pidfile, "w")
        f.write(str(os.getpid()))
        f.close()
        scaler.start()
        os.unlink(opt.pidfile)
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.monitor:
    if opt.id != None:
        print "Adding an alarm definition to instance %s" % opt.id
        scaler = AutoScaler()
        scaler.monitor_instance(opt.id, cputhres=opt.thres, period=opt.period)
        if opt.lbname != None:
          print "Adding instance %s to loadbalancer %s" % (opt.id, opt.lbname)
          scaler = AutoScaler()
          elb = scaler.connect_elb()
          elb.register_instances(opt.lbname, [opt.id])
          #does not work
          #elb.enable_availability_zones(opt.lbname, [os.environ['EC2_LB_AZ']])
    elif opt.lbname != None:
        print "Adding an alarm definition to load balancer %s" % opt.lbname
        scaler = AutoScaler()
        scaler.monitor_loadbalancer(opt.lbname, reqthres=opt.thres)
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.alarm_state:
  (name,alarm_state) = opt.alarm_state.split('/')
  if name!='' and alarm_state != '':
        print "Setting alarm state for %s to %s" % (name, alarm_state)
        scaler = AutoScaler()
        scaler.simulate_alarm(name, alarm_state)
  else:
        print "Require a valid name:state string"
        exit(-1)

if opt.ping:
    if opt.id != None:
        inst = mgr.get_instance(opt.id)
        try:
            pingURL = "http://%s:%s/ping" % (inst.public_dns_name,
                                             os.environ['KAS_PORT'])
            print "Worker-Ping at %s" % pingURL
            urllib2.urlopen(pingURL)
            print "OK"

            pingURL = "http://%s:%s/ping" % (inst.public_dns_name,
                                             os.environ['KAS_SCALER_PORT'])
            print "Scaler-Ping at %s" % pingURL
            urllib2.urlopen(pingURL)
            print "OK"
        except Exception as e:
            print "Ping error %s" % e
    else:
        print "Require a valid instance id"
        exit(-1)

if opt.scaleup:
        scaler = AutoScaler()
        scaler.scale_up()

if opt.scaledown:
        scaler = AutoScaler()
        scaler.scale_down('*')
    