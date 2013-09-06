# AutoScaler for Amazon AWS
# (c) 2013 Patrick Senti
# patrick dot senti at gmx dot net

__author__="patrick"
__date__ ="$Feb 3, 2013 8:16:21 AM$"

from workermgr import KooabaWorkerManager
from boto.ec2.cloudwatch import CloudWatchConnection
from boto.ec2.cloudwatch.alarm import MetricAlarm
from boto.ec2 import cloudwatch
from boto import sns
from boto.ec2 import elb
from workermgr import *
from common import *

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import httplib
import urllib2
import socket
import json
import os

class AutoScalerHandler(BaseHTTPRequestHandler):
    '''
    Processes the SubscribtionConfirmation, Notification and
    UnsubscribeConfirmation messages sent by SNS. It handles the
    confirmation and unsubscription messages by itself (see URL below).
    Upon receiving a Notification it creates and AutoScaler instance
    and sends it the processAlarm message

    see http://docs.aws.amazon.com/sns/latest/gsg/json-formats.html
    '''
    def do_POST(self):
        '''
        Receivs the notification from CloudWatch through SNS. This
        method determines the message type, then calls the respective
        process_xyz method, respectively.
        '''
        try:
            # get message type and topic
            msgtype = self.headers['x-amz-sns-message-type']
            topic = self.headers['x-amz-sns-topic-arn']
            # get body
            content_len = int(self.headers.getheader('content-length'))
            body = self.rfile.read(content_len)
            # process message
            if msgtype == 'SubscriptionConfirmation':
                self.log_message("Received confirmation request for topic %s", topic)
                self.process_confirmation(json.loads(body))
            elif msgtype == 'Notification':
                self.log_message("Received notification for topic %s", topic)
                self.process_notification(json.loads(body))
            elif msgtype == 'UnsubscribeConfirmation':
                self.log_message("Received unsubscribe request for topic %s", topic)
                self.process_unsubscribe(json.loads(body))
            # if all went well let them know
            self.respond(200, 'accepted')
        except Exception, e:
            self.log_message('Invalid request received\%s\%s', self.headers, e)
            self.send_error(400)

    def process_confirmation(self, msg):
        '''
        process a SubscriptionConfirmation message. Extracts the
        URL provided and opens it to confirm the subscription
        '''
        subURL = msg['SubscribeURL']
        try:
            urllib2.urlopen(subURL)
        except urllib2.URLError as e:
            self.log_message('Error %s calling %s' % (e, subURL))

    def process_notification(self, msg):
        '''
        Process a notification. This creates an AutoScaler instance, then
        calls its process_notification method to determine the scaling
        activity, if any.
        
        The notification is a JSON message string as follows. We only
        forward the name, state and previous state
        {u'SignatureVersion': u'1',
         u'Timestamp': u'2013-02-03T16:17:45.364Z',
         u'Signature': u'E3aFfxfXPSHWZcVoScdOa6arbq8wkqmRxyBzpmsK/5xKW9UnWM/AS/UrjgAp5AghlHIwxzRi9DFpcCInaOIOcBInhLHEfjNaDKvvQVvmJQcOauymA04yt1lv9EIvBis1EVuz/x4SeISlvk1EBY16TGitxAViU7pC7TyMK3wspH0=',
         u'SigningCertURL': u'https://sns.eu-west-1.amazonaws.com/SimpleNotificationService-f3ecfb7224c7233fe7bb5f59f96de52f.pem',
         u'MessageId': u'69814f58-e83d-5844-b387-06d067d41aa6',
         u'Message': u'{"AlarmName":"OhHo4oop:cpuhigh:i-24be746e",
                        "AlarmDescription":"Automatic metric",
                        "AWSAccountId":"237471159969",
                        "NewStateValue":"OK",
                        "NewStateReason":"Test state",
                        "StateChangeTime":"2013-02-03T16:17:45.322+0000",
                        "Region":"EU - Ireland",
                        "OldStateValue":"INSUFFICIENT_DATA",
                        "Trigger":{"MetricName":"CPUUtilization",
                                   "Namespace":"None",
                                   "Statistic":"AVERAGE",
                                   "Unit":"Percent",
                                   "Dimensions":[{"name":"InstanceId","value":"i-24be746e"}],
                                   "Period":60,"EvaluationPeriods":1,
                                   "ComparisonOperator":"GreaterThanOrEqualToThreshold",
                                   "Threshold":35.0}}',
         u'UnsubscribeURL': u'https://sns.eu-west-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop:afa96aa6-2cbc-4feb-87f0-1a330015be52',
         u'Type': u'Notification',
         u'TopicArn': u'arn:aws:sns:eu-west-1:237471159969:autoscale-OhHo4oop',
         u'Subject': u'OK: "OhHo4oop-cpuhigh-i-24be746e" in EU - Ireland'}
        '''
        #self.log_message("Processing Notification msg %s", msg)
        body = json.loads(msg['Message'])
        name = body['AlarmName']
        state = body['NewStateValue']
        prev_state = body['OldStateValue']
        AutoScaler().process_notification(name, state, prev_state)

    def process_unsubscribe(self, msg):
        '''
        process the UnsubscribeConfirmation. Reads the provided URL
        and opens it to confirm the unsubscription.
        '''
        subURL = msg['SubscribeURL']
        try:
            urllib2.urlopen(subURL)
        except urllib2.URLError as e:
            self.log_message('Error %s calling %s' % (e, subURL))

    def do_GET(self):
        '''
        implements a simple ping
        '''
        if self.path == '/ping':
            self.respond(httplib.OK, 'pong')
        else:
            self.respond(httplib.NOT_FOUND, "not found")

    def respond(self, code, text):
        """ Respond with a text. """
        self.send_response(code)
        self.send_header('Content-Type', 'text/plain')
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    # this copied from the provided worker script (server.py)
    # we override log_message() to show which process is handling the request
    def log_message(self, format, *args):
        note(format, *args)

  
class AutoScaler:
    '''
    Implements the autoscaler component. It interfaces with the ELB
    and CloudWatch services. ELB is used to add/remove started/stopped
    instances, and CloudWatch is used to register alarms. The class
    provides several methods to simplify addition and listing of information
    provided by CloudWatch and ELB.
    '''
    def init(self):
        '''
        Connect to cloudwatch.
        TODO refactor to connect_cloudwatch
        '''
        try:
            for reg in cloudwatch.regions():
                if(reg.name == os.environ['AWS_DEFAULT_REGION']):
                    return CloudWatchConnection(region=reg)
            return None
        except Exception as e:
            print "%s" % e
            exit(-1)

    def connect_sns(self):
        '''
        Connect to SNS
        '''
        try:
            for reg in sns.regions():
                if(reg.name == os.environ['AWS_DEFAULT_REGION']):
                    return sns.connect_to_region(reg.name)
            return None
        except Exception as e:
            print "%s" % e
            exit(-1)

    def connect_elb(self):
        '''
        Connect to ELB
        '''
        try:
            for reg in elb.regions():
                if(reg.name == os.environ['AWS_DEFAULT_REGION']):
                    return elb.connect_to_region(reg.name)
            return None
        except Exception as e:
            print "%s" % e
            exit(-1)

    def get_alarms(self):
        '''
        retrieves all alarms for the current account
        '''
        conn = self.init()
        alarms = conn.describe_alarms()
        return alarms

    def get_loadbalancers(self):
        '''
        retrieves all loadbalancers for the current account
        '''
        lb = self.connect_elb()
        return lb.get_all_load_balancers()

    def alarm_name(self, type, dimension):
        '''
        creates a standardizes alarm name, which has the following
        format:

        LOADBALANCER:TYPE:DIMENSION

        where LOADBALANCER is the name of the LB
              TYPE is the alarm type (e.g. cpuhigh, cpulow)
              DIMENSION is the id of the respective resource (e.g. instance or
              loadbalancer)
        '''
        return "%s:%s:%s" % (os.environ['KAS_KEY'], type, dimension)

    def parse_alarm_name(self, name):
        '''
        parses an alarm name into its components, see alarm_name
        '''
        print name.split(':')
        return name.split(':')

    def monitor_instance(self, instid, cputhres=None, period=None):
        '''
        Adds an instance to CloudWatch, generating cpuhigh and cpulow
        alarms.
        '''
        conn = self.init()
        # default threshold
        if cputhres is None:
            cputhres = os.environ['KAS_ALARM_CPUTHRES']
        if period is None:
            period = os.environ['KAS_WATCH_PERIOD']
        cpulow = float(cputhres.split(':')[0])
        cpuhigh = float(cputhres.split(':')[1])
        #create a metric for cpu high for this instance
        alarm = MetricAlarm(name=self.alarm_name('cpuhigh', instid),
                            metric='CPUUtilization',
                            statistic='Average',
                            namespace="AWS/EC2",
                            dimensions={'InstanceId':[instid]},
                            comparison='>=',
                            threshold=cpuhigh,
                            evaluation_periods=1,
                            description='Automatic metric',
                            alarm_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            ok_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            period=int(period))
        conn.put_metric_alarm(alarm)
        # create a metric for cpu high for this instance
        alarm = MetricAlarm(name=self.alarm_name('cpulow', instid),
                            metric='CPUUtilization',
                            statistic='Average',
                            namespace="AWS/EC2",
                            dimensions={'InstanceId':[instid]},
                            comparison='>=',
                            threshold=cpulow,
                            evaluation_periods=1,
                            description='Automatic metric',
                            alarm_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            ok_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            period=int(period))
        conn.put_metric_alarm(alarm)

    def monitor_loadbalancer(self, name, reqthres=None):
        conn = self.init()
        # default threshold
        if reqthres is None:
            reqthres = 1.0
        # create a metric for request count this instance
        alarm = MetricAlarm(name=self.alarm_name('reqcount', name),
                            metric='Latency',
                            statistic='Average',
                            dimensions={'LoadBalancerName':[name]},
                            namespace="AWS/EC2",
                            comparison='>=',
                            threshold=reqthres,
                            unit='Count',
                            evaluation_periods=1,
                            description='Automatic metric',
                            alarm_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            ok_actions=os.environ['KAS_SNS_TOPIC_ARN'],
                            period=300)
        conn.put_metric_alarm(alarm)
    
    def set_url(self, monitorurl):
        snsconn = self.connect_sns()
        # remove any previous subscriptions
        try:
            # unsubscribe
            snsconn.unsubscribe(os.environ['KAS_SNS_TOPIC_ARN'])
            # subscribe this instance to the topic
            scalerURL = "http://%s:%s" % (monitorurl, os.environ['KAS_SCALER_PORT'])
            snsconn.subscribe(os.environ['KAS_SNS_TOPIC_ARN'], 'http', scalerURL)
        except Exception as e:
            note("Failure to subscribe topic %s, %s", os.environ['KAS_SNS_TOPIC_ARN'], e)
        
    def remove_monitor_instance(self, instid):
        conn = self.init()
        conn.delete_alarms([self.alarm_name('cpuhigh', instid)])

    def start(self):
        address = ('localhost', int(os.environ['KAS_SCALER_PORT_INTERN']))
        server = HTTPServer(address, AutoScalerHandler)
        note('Started AutoScale instance on port %s', address[1])
        server.serve_forever()

    def process_notification(self, name, state, prev_state):
        self.init()
        key,type,id = self.parse_alarm_name(name)
        if type == 'cpuhigh':
            note('Notification for cpuhigh %s on instance %s', state, id)
            if state == 'ALARM':
                return self.scale_up()
            if state == 'OK':
                return None
        if type == 'cpulow':
            note('Notification for cpulow %s on instance %s', state, id)
            if state == 'OK':
                return self.scale_down(id)
            if state == 'ALARM':
                return None
        if type == 'reqcount':
            note('Notification for reqcount %s on loadbalancer %s', state, id)
            if state == 'ALARM':
                return self.scale_up()
            elif state == 'OK':
                return self.scale_down('*')
        # none processed, something has gone wrong
        note('Invalid notification type %s', type)
        return None
                
    def scale_up(self):
        '''
        Find a stopped instance that can be started, i.e. any instance
        that matches the KAS_KEYFILTER and is either stopping or
        stopped. Only starts one instance at a time.
        '''
        try:
            mgr = KooabaWorkerManager()
            list = mgr.get_instances(key_name=os.environ['KAS_KEYFILTER'])
            for id in list:
                inst = list[id]
                if inst.state == 'stopped':
                    note('Trying to start instance %s', inst.id)
                    inst.start()
                    note('Adding instance %s to load balancer', inst.id)
                    elb = self.connect_elb()
                    elb.register_instances(os.environ['KAS_KEY'], [inst.id])
                    # FIXME not a good idea, it resets the manual triggers
                    # make sure the instance is monitored
                    # self.monitor_instance(inst.id)
                    return inst.id
            # no instance found thus far
            note('No instance available to start')
            return None
        except Exception as e:
            note('Error starting an instance, %s', e)

    def scale_down(self, instid):
        '''
        Stop instid. Note this does not stop an instance if its
        name is <KeyName>_base. If instid is '*', will attempt to
        stop the first running instance it encounters.
        '''
        mgr = KooabaWorkerManager()
        try:
            if instid == '*':
                list = mgr.get_instances(key_name=os.environ['KAS_KEYFILTER'])
                for id in list:
                    inst = list[id]
                    if self.scale_down_instance(inst) != None:
                        return inst.id
                note('No running instance to scale down. Hence terminating all stopped.')
                for id in list:
                    inst = list[id]
                    if inst.state == 'stopped':
                        mgr.terminate_instance(inst.id)
                        elb = self.connect_elb()
                        elb.deregister_instances(os.environ['KAS_KEY'], [inst.id])
                return 'terminated.all'
            else:
                inst = mgr.get_instance(instid)
                # if none was scaled down (probably base or ctl), shut down
                # any
                if self.scale_down_instance(inst) == None:
                   instid = self.scale_down('*')
                return instid
        except Exception as e:
            note('Error stopping instance %s, %s', instid, e)
        return None

    def scale_down_instance(self, inst):
        '''
        Scale down a particular instance. Checks for _base and _ctl
        instances, which are never scaled down. Only instances in
        running state are scaled down after being removed from the ELB.
        TODO stopping should happen in background thread a few minutes
        after removing of ELB was successfull
        '''
        if inst.name != "%s_base" % os.environ['KAS_KEY'].strip() and \
           inst.name != "%s_ctl" % os.environ['KAS_KEY'].strip():
            if inst.state == 'running':
                note('Removing instance %s form load balancer', inst.id)
                elb = self.connect_elb()
                elb.deregister_instances(os.environ['KAS_KEY'], [inst.id])
                note('Stopping instance %s', inst.id)
                inst.stop()
                return inst.id
        else:
            note('Not scaling down instance %s which is the base', inst.id)
        return None

    def simulate_alarm(self, name, state):
        '''
        Sets the CloudWatch alarm state to issue a SNS notification
        The alarm name must be given as known to CloudWatch
        '''
        conn = self.init()
        conn.set_alarm_state(name, 'Test state', state)