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

Slack with vaulted token
------------------------

This plugins (``vaulted_slack``) posts playbook result on `Slack`_ using a token stored
in a vaulted file.

The token location should be in the ``token_key`` key of the ``vaulted-slack`` section
of the Ansible configuration file and follow the ``<vaulted_filename>#<variable>`` pattern.

.. code-block:: ini

    [vaulted-slack]
    token-key = ./path/to/my/vault#parent.token

.. _Slack: https://slack.com/
