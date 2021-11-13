import subprocess
import shlex

from .exceptions import SindriSupplierNotFound, SindriSupplierFailedError

def get_subdomains(domain):
    amass_command = ["amass", "enum", "-nocolor", "-passive", "-d", domain]
    print(f"Running amass: {shlex.join(amass_command)}")
    try:
        amass_process = subprocess.Popen(amass_command, stdout=subprocess.PIPE)
    except FileNotFoundError:
        raise SindriSupplierNotFound()

    amass_process.wait()
    if amass_process.returncode != 0:
        raise SindriSupplierFailedError(f"Return code: {amass_process.returncode}")
    return amass_process.stdout.read().decode().strip().splitlines()


