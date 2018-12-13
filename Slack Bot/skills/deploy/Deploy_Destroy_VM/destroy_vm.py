from subprocess import *
import sys
import argparse
import os

def destroy():
    os.environ["VSPHERE_SERVER"]="vcenter.bluecatlabs.net"
    os.environ["VSPHERE_USER"]="bclsvcintegritybot@bluecatlabs.net"
    os.environ["VSPHERE_PASSWORD"]="eeBieF2eeth7qui!yeexai(S7hae2O"
    os.environ["VSPHERE_ALLOW_UNVERIFIED_SSL"]="true"

    state_file = '/home/ubuntu/bpcbot/skills/deploy/Deploy_Destroy_VM/terraform.tfstate'
    if os.path.exists(state_file):
        terraform_destroy_cmd = 'terraform destroy -auto-approve -state='+state_file
        call(terraform_destroy_cmd, shell=True)
    else:
        print("No state file found. Reference deleted !!! Please delete manually")

if __name__ == "__main__":
    sys.exit(destroy())
