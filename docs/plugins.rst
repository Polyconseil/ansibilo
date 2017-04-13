Ansible callback plugins
========================

Callback modules are activated by adding their name in the
``defaults.callback_whitelist`` key of the ansible config file.

Pretty print result
-------------------

This plugin (``pretty_print_result``) prints task result in indented format.

Git branch up to date
---------------------

This plugins (``git_branch_uptodate``) stops the playbook execution if your
local branch is not up to date with the origin branch.
