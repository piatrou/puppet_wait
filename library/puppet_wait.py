#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess

from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
module: puppet_wait
short_description: Wait puppet
options: 
  repeat:
    description:
      - Repeat count
'''

EXAMPLES = '''
- name: Wait puppet
  puppet_wait:
    repeat: 0
'''

class PuppetAgent:
    changed = False
    failed = False


    def test(self)->bool:
        with subprocess.Popen('sudo puppet agent -t', shell=True, stdout=subprocess.PIPE) as popen:
            status = popen.wait()
            stdout,_ = popen.communicate()
            self.failed = status != 0
            if self.failed:
                return False

            for line in stdout.split('\n'):
                if line[:6] == 'Error':
                    self.failed = True
                    return False
                if line[:6] == 'Notice' and line[8:15] != 'Applied':
                    self.changed = True
                    return True
        return False

def main():
    module = AnsibleModule(
        argument_spec={
            "repeat": {
                "required": False,
                "default": 0
            },
        },
        supports_check_mode=True
    )

    agent = PuppetAgent()
    repeat = 0
    if module.params['repeat']:
        repeat = int(module.params['repeat'])
    if repeat <= 0:
        while agent.test():
            pass
    for _ in range(repeat):
        agent.test()

    if agent.failed:
        raise Exception('Puppet agent failed!')

    result = {
        'changed': agent.changed,
    }

    module.exit_json(**result)

if __name__ == '__main__':
    main()
