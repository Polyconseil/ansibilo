facto - secrets and ports management
====================================

``facto`` is an Ansible module with two main function:
  - generate secrets on the remote host and store them for future runs
  - select an unused port on the remote host and reserve it for future runs

Secret generation
-----------------

.. code-block:: yaml

    - name: Remotely generated secret
      facto:
        key: my-secret  # the secret name
        kind: secret
        fact: my_secret  # store the secret in this variable

    - name: Use secret
      file:
        content: "passwd = {{ my_secret }}"
        dest: /my/config/path

TCP or UDP port reservation
---------------------------

.. code-block:: yaml

    - name: Remotely generated secret
      facto:
        key: my-port  # the secret name
        kind: tcp-port  # or udp-port
        fact: my_port  # store the port number in this variable
