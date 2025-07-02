from django.core import management

def dbbackup_q2():
    management.call_command('dbbackup', '--clean')
    management.call_command('mediabackup', '--clean')
