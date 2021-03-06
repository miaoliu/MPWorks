import time
from fireworks.core.firework import FireTaskBase, FWAction, FireWork, Workflow
from fireworks.utilities.fw_serializers import FWSerializable
from fireworks.utilities.fw_utilities import get_slug
from mpworks.dupefinders.dupefinder_vasp import DupeFinderVasp
from mpworks.firetasks.custodian_task import get_custodian_task
from mpworks.firetasks.vasp_io_tasks import VaspCopyTask, VaspToDBTask
from mpworks.firetasks.vasp_setup_tasks import SetupStaticRunTask, \
    SetupNonSCFTask
from mpworks.workflows.wf_settings import QA_VASP, QA_DB
from pymatgen import Composition
from pymatgen.matproj.snl import StructureNL

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'May 01, 2013'


class AddEStructureTask_old(FireTaskBase, FWSerializable):
    _fw_name = "Add Electronic Structure Task"

    def __init__(self, parameters=None):
        """

        :param parameters:
        """
        parameters = parameters if parameters else {}
        self.update(parameters)  # store the parameters explicitly set by the user
        self.gap_cutoff = parameters.get('gap_cutoff', 0.5)  # see e-mail from Geoffroy, 5/1/2013

    def run_task(self, fw_spec):
        print 'sleeping 10s for Mongo'
        time.sleep(10)
        print 'done sleeping'
        print 'the gap is {}, the cutoff is {}'.format(fw_spec['analysis']['bandgap'], self.gap_cutoff)

        if fw_spec['analysis']['bandgap'] >= self.gap_cutoff:
            print 'Adding more runs...'
            type_name = 'GGA+U' if 'GGA+U' in fw_spec['prev_task_type'] else 'GGA'

            snl = StructureNL.from_dict(fw_spec['mpsnl'])
            f = Composition.from_formula(snl.structure.composition.reduced_formula).alphabetical_formula

            fws = []
            connections = {}

            priority = fw_spec['_priority']

            # run GGA static
            spec = fw_spec  # pass all the items from the current spec to the new
            #  one
            spec.update({'task_type': '{} static'.format(type_name), '_queueadapter': QA_VASP,
                         '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority})
            fws.append(
                FireWork(
                    [VaspCopyTask({'use_CONTCAR': True}), SetupStaticRunTask(),
                     get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-10))

            # insert into DB - GGA static
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(
                FireWork([VaspToDBTask()], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-9))
            connections[-10] = -9

            # run GGA Uniform
            spec = {'task_type': '{} Uniform'.format(type_name), '_queueadapter': QA_VASP,
                    '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority}
            fws.append(FireWork(
                [VaspCopyTask({'use_CONTCAR': False}), SetupNonSCFTask({'mode': 'uniform'}),
                 get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-8))
            connections[-9] = -8

            # insert into DB - GGA Uniform
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(
                FireWork([VaspToDBTask({'parse_uniform': True})], spec, name=get_slug(f+'--'+spec['task_type']),
                         fw_id=-7))
            connections[-8] = -7

            # run GGA Band structure
            spec = {'task_type': '{} band structure'.format(type_name), '_queueadapter': QA_VASP,
                    '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority}
            fws.append(FireWork([VaspCopyTask({'use_CONTCAR': False}), SetupNonSCFTask({'mode': 'line'}),
                                 get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']),
                                fw_id=-6))
            connections[-7] = -6

            # insert into DB - GGA Band structure
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(FireWork([VaspToDBTask({})], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-5))
            connections[-6] = -5

            wf = Workflow(fws, connections)

            print 'Done adding more runs...'

            return FWAction(additions=wf)
        return FWAction()


class AddEStructureTask(FireTaskBase, FWSerializable):
    _fw_name = "Add Electronic Structure Task v2"

    def __init__(self, parameters=None):
        """

        :param parameters:
        """
        parameters = parameters if parameters else {}
        self.update(parameters)  # store the parameters explicitly set by the user
        self.gap_cutoff = parameters.get('gap_cutoff', 0.5)  # see e-mail from Geoffroy, 5/1/2013

    def run_task(self, fw_spec):
        print 'sleeping 10s for Mongo'
        time.sleep(10)
        print 'done sleeping'
        print 'the gap is {}, the cutoff is {}'.format(fw_spec['analysis']['bandgap'], self.gap_cutoff)

        if fw_spec['analysis']['bandgap'] >= self.gap_cutoff:
            print 'Adding more runs...'
            type_name = 'GGA+U' if 'GGA+U' in fw_spec['prev_task_type'] else 'GGA'

            snl = StructureNL.from_dict(fw_spec['mpsnl'])
            f = Composition.from_formula(snl.structure.composition.reduced_formula).alphabetical_formula

            fws = []
            connections = {}

            priority = fw_spec['_priority']

            # run GGA static
            spec = fw_spec  # pass all the items from the current spec to the new
            #  one
            spec.update({'task_type': '{} static v2'.format(type_name), '_queueadapter': QA_VASP,
                         '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority})
            fws.append(
                FireWork(
                    [VaspCopyTask({'use_CONTCAR': True}), SetupStaticRunTask(),
                     get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-10))

            # insert into DB - GGA static
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(
                FireWork([VaspToDBTask()], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-9))
            connections[-10] = -9

            # run GGA Uniform
            spec = {'task_type': '{} Uniform v2'.format(type_name), '_queueadapter': QA_VASP,
                    '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority}
            fws.append(FireWork(
                [VaspCopyTask({'use_CONTCAR': False}), SetupNonSCFTask({'mode': 'uniform'}),
                 get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-8))
            connections[-9] = -8

            # insert into DB - GGA Uniform
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(
                FireWork([VaspToDBTask({'parse_uniform': True})], spec, name=get_slug(f+'--'+spec['task_type']),
                         fw_id=-7))
            connections[-8] = -7

            # run GGA Band structure
            spec = {'task_type': '{} band structure v2'.format(type_name), '_queueadapter': QA_VASP,
                    '_dupefinder': DupeFinderVasp().to_dict(), '_priority': priority}
            fws.append(FireWork([VaspCopyTask({'use_CONTCAR': False}), SetupNonSCFTask({'mode': 'line'}),
                                 get_custodian_task(spec)], spec, name=get_slug(f+'--'+spec['task_type']),
                                fw_id=-6))
            connections[-7] = -6

            # insert into DB - GGA Band structure
            spec = {'task_type': 'VASP db insertion', '_queueadapter': QA_DB,
                    '_allow_fizzled_parents': True, '_priority': priority}
            fws.append(FireWork([VaspToDBTask({})], spec, name=get_slug(f+'--'+spec['task_type']), fw_id=-5))
            connections[-6] = -5

            wf = Workflow(fws, connections)

            print 'Done adding more runs...'

            return FWAction(additions=wf)
        return FWAction()


class DummyLegacyTask(FireTaskBase, FWSerializable):
    _fw_name = "Dummy Legacy Task"

    def run_task(self, fw_spec):
        pass