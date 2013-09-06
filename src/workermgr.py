# AutoScaler for Amazon AWS
# (c) 2013 Patrick Senti
# patrick dot senti at gmx dot net


__author__="patrick"
__date__ ="$Feb 3, 2013 8:07:21 AM$"

from boto import ec2
import os

if __name__ == "__main__":
    print "Hello World"


class KooabaWorkerManagerDryRun:
    '''
    Mocks a simple interface to AWS EC2. Exposes
    methods to retrieve instances, create an instance
    and terminate an instances.
    '''
    def init(self):
        print "dry: Creating EC2 Connection"

    def dummy_instance(self):
        return inst

    def create_instance(selfs):
        print "dry: Creating instance"
        return DummyInstance()

    def get_instances(self):
        list = {}
        for i in range(5):
            list[i] = DummyInstance()
        return list

    def terminate_instance(self, id):
        print "dry: Terminating instance id=%s name=%s" % (id, name)



class KooabaWorkerManager:
    '''
    Implements a simple interface to AWS EC2. Exposes
    methods to retrieve instances, create an instance
    and terminate an instances.
    '''
    def init(self):
        '''
        Create a connection to EC2
        TODO refactor to connect_ec2
        '''
        #print "Creating EC2 Connection"
        try:
            for reg in ec2.regions():
                if(reg.name == os.environ['AWS_DEFAULT_REGION']):
                    return reg.connect()
        except Exception as e:
            print "%s" % e
        return None

    def create_instance(self):
        '''
        Adds a new instance (run_instance) in running state.
        The instance is based on the following env variables:
        AWS_DEFAULT_AMI  the ami
        KAS_KEY          the name of the .pem file
        EC2_LB_AZ        Loadbalancer Az name
        The name of the instance is KAS_KEY + the newly assigned
        instance id
        '''
        conn = self.init()
        print "Creating instance"
        try:
            # create the instance
            res = conn.run_instances(os.environ['AWS_DEFAULT_AMI'],
                               key_name='OhHo4oop',
                               placement=os.environ['EC2_LB_AZ'],
                               instance_type='m1.small',
                               security_groups=['job-test'])
            inst = res.instances[0]
            # set the name tag
            tags = {'Name':"%s-%s" % (os.environ['KAS_KEY'],inst.id) }
            conn.create_tags(inst.id, tags)
            return inst
        except Exception as e:
            print "%s" % e
            return None

    def get_instance(self, id):
        '''
        retrieves a single instance
        returns an boto EC2Instance
        '''
        conn = self.init()
        try:
            list = self.get_instances()
            return list[id]
        except Exception as e:
            print "Error retrieving instance %s, %s" % (id, e)
            return []

    def get_instances(self, key_name=None):
        '''
        retrieves all instances, filtered by key_name
        '''
        conn = self.init()
        list = {}
        tags = self.get_tags()
        try:
            instances = conn.get_all_instances()
            # we get a list of Reservations
            for res in instances:
                for inst in res.instances:
                    if key_name is None or key_name == inst.key_name:
                        list[inst.id] = inst
                        inst.name = ''
                        if inst.id in tags:
                            tagmap = tags[inst.id]
                            if 'Name' in tagmap:
                                inst.name = tagmap['Name']
                            else:
                                inst.name = ''
            return list
        except Exception as e:
            print "Error retrieving instances key=%s, %s" % (key_name, e)
            return []

    def terminate_instance(self, id):
        '''
        terminates an instance
        '''
        print "Terminating instance id=%s" % id
        inst = self.get_instance(id)
        try:
            inst.terminate()
        except Exception as e:
            print "%s" % e
            

    def get_tags(self):
        '''
        returns a dict of instance tags, per instance id
        every tag contains the following attributes
        res_type, res_id, name, value
        '''
        conn = self.init()
        metatags = conn.get_all_tags()
        inst_tags = {}
        for tag in metatags:
            if tag.res_type == 'instance':
                if tag.res_id in inst_tags:
                    map = inst_tags[tag.res_id]
                else:
                    map = {}
                    inst_tags[tag.res_id] = map
                map[tag.name] = tag.value
        return inst_tags
