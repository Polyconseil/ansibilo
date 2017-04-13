# -*- coding: utf-8 -*-
import errno
import os
import subprocess

from ansible.plugins.callback import CallbackBase


class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'git_branch_uptodate'
    CALLBACK_NEEDS_WHITELIST = True

    def playbook_on_play_start(self, name):
        if 'VAGRANT_EXECUTABLE' in os.environ.keys():
            print("Playbook '%s' started on Vagrant. You're probably not up to date." % name)
            return
        try:
            # Redirect distracting output to /dev/null
            with open(os.devnull, 'w') as devnull:
                # Fetch remote refs
                subprocess.check_call('git remote update'.split(), stdout=devnull)
            # Fetch master commit id
            upstream_master = subprocess.check_output('git rev-parse master@{u}'.split())
            # Fetch the commit id that is the base of the divergence between our
            # branch and master (if there is any)
            base = subprocess.check_output('git merge-base @ master@{u}'.split())
            # master is not the base of the divergence, thus we are either
            # right behind it, or in another branch that's missing some commits
            if base != upstream_master:
                print("Your local branch is not in sync with master, please update.")
                os.sys.exit(errno.EPERM)
        except subprocess.CalledProcessError as e:
            print("Failed to interact with git, unsafe to continue (retcode: %d)" % e.returncode)
            os.sys.exit(errno.EPERM)
