import subprocess
import shlex
import os

from .exceptions import SindriSupplierNotFound, SindriSupplierFailedError
from .consts import SINDRI_CONFIG

def get_subdomains(domain):
    config_path = os.getenv("AMASS_CONFIG", os.path.join(SINDRI_CONFIG, "amass.ini"))
    if os.path.exists(config_path):
        amass_command = ["amass", "enum", "-config", config_path , "-nocolor", "-passive", "-d", domain]
    else:
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


