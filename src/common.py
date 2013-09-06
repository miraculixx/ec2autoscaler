import sys
import datetime
from multiprocessing import Process, current_process, freeze_support

def note(format, *args):
    now = datetime.datetime.now()
    current_time= now.strftime("%Y-%m-%d %H:%M")
    sys.stderr.write('%s [%s]\t%s\n' % (current_time,
                                        current_process().name, format%args))
    sys.stderr.flush()