import json
import logging
import os
import sys
from pymongo import MongoClient
from fireworks.core.launchpad import LaunchPad
from mpworks.drones.mp_vaspdrone import MPVaspDrone
import multiprocessing
import traceback

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Jun 13, 2013'


__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'May 13, 2013'

class TaskBuilder():

    @classmethod
    def setup(cls):
        db_dir = os.environ['DB_LOC']
        db_path = os.path.join(db_dir, 'tasks_db.json')
        with open(db_path) as f2:
            db_creds = json.load(f2)
            mc2 = MongoClient(db_creds['host'], db_creds['port'])
            db2 = mc2[db_creds['database']]
            db2.authenticate(db_creds['admin_user'], db_creds['admin_password'])

            cls.tasks = db2['tasks']
            cls.host = db_creds['host']
            cls.port = db_creds['port']
            cls.database = db_creds['database']
            cls.collection = db_creds['collection']
            cls.admin_user = db_creds['admin_user']
            cls.admin_password = db_creds['admin_password']

    def process_task(self, data):
        try:
            dir_name = data[0]
            parse_dos = data[1]
            drone = MPVaspDrone(
                host=self.host, port=self.port,
                database=self.database, user=self.admin_user,
                password=self.admin_password,
                collection=self.collection, parse_dos=parse_dos,
                additional_fields={},
                update_duplicates=True)
            t_id, d = drone.assimilate(dir_name, launches_coll=LaunchPad.auto_load().launches)
            print 'FINISHED', t_id
        except:
            print '-----'
            print 'ENCOUNTERED AN EXCEPTION!!!', data[0]
            traceback.print_exc()
            print '-----'


def _analyze(data):
    b = TaskBuilder()
    return b.process_task(data)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('MPVaspDrone')
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setLevel(getattr(logging, 'INFO'))
    logger.addHandler(sh)

    o = TaskBuilder()
    o.setup()
    tasks = TaskBuilder.tasks
    m_data = []
    q = {'submission_id': {'$exists': False}}  # these are all new-style tasks
    for d in tasks.find(q, {'dir_name_full': 1, 'task_id': 1, 'task_type': 1}):
        m_data.append((d['dir_name_full'], 'Uniform' in d['task_type']))
    print 'GOT all tasks...'
    pool = multiprocessing.Pool(16)
    pool.map(_analyze, m_data)
    print 'DONE'