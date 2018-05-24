#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xperiment.settings.local")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

    if 'SERVERTYPE' not in os.environ or os.environ['SERVERTYPE'] != 'AWS Lambda':
        import json

        #json_data = open('zappa_settings.json')
        #env_vars = json.load(json_data)['dev']['environment_variables']
        #for key, val in env_vars.items():
        #    os.environ[key] = val
