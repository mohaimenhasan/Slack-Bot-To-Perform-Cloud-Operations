#!/usr/bin/env python

from __future__ import print_function
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import atexit
import sys
import argparse
import ssl
import humanize

def get_all_objs(content, vimtype, folder=None, recurse=True):
    """
    Returns all Objects of type
    """
    if not folder:
        folder = content.rootFolder

    obj = {}
    container = content.viewManager.CreateContainerView(folder, vimtype, recurse)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj

def find_datacenter(content, name=None):
    """
    Finds the datacenter by name
    """
    if not name:
        return content.rootFolder.childEntity[0]

    for datacenter in content.rootFolder.childEntity:
        if datacenter.name == name:
            return datacenter
    return None

def find_folder(content, path, datacenter=None):
    """
    Finds the Folder Object based on the path
    :param content:
    :param path:
    :param datacenter:
    :return:
    """
    folder_names = filter(lambda x: x != '', path.split('/'))
    datacenter = find_datacenter(content, datacenter)
    folder = datacenter.vmFolder

    for name in folder_names:
        found = False
        for child in folder.childEntity:
            if child.name == name:
                folder = child
                found = True
                break
        if not found:
            return None
    return folder

def GetVMs(content):
    print("Getting all VMs ...")
    try:
        vm_view = content.viewManager.CreateContainerView(content.rootFolder,
                                                      [vim.VirtualMachine],
                                                      True)
    except Exception as error:
        print(error)
        pass
    obj = [vm for vm in vm_view.view]
    vm_view.Destroy()
    return obj


def GetArgs():

    parser = argparse.ArgumentParser(
        description='Process args for retrieving all the Virtual Machines')
    parser.add_argument('-host', '--host', required=True, action='store',
                        help='Remote host to connect to')
    parser.add_argument('-port', '--port', type=int, default=443, action='store',
                        help='Port to connect on')
    parser.add_argument('-user', '--user', required=True, action='store',
                        help='User name to use when connecting to host')
    parser.add_argument('-password', '--password', required=False, action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-SSL', '--disable_ssl_verification',
                        required=False,
                        action='store',
                        type=bool,
                        default=False,
                        help='Disable ssl host certificate verification')
    parser.add_argument('-path', '--path', required=False, action='store',
                        help="""List path of a particular folder on BPC.
                        Structure should be:
                        Tenants-Internal/<Pool>/<Location>""")
    parser.add_argument('-team', '--team', required=False, action='store',
                        help='List your team')
    parser.add_argument('-product', '--product', required=False, action='store',
                        help='List your product')
    parser.add_argument('-folder', '--folder', required=False, action='store',
                        help='List your folder under a team')
    args = parser.parse_args()
    return args

def main():
    global content, hosts, hostPgDict
    args = GetArgs()
    sslContext = None
    SSLVerification = False

    if args.path is None and (args.product and args.team) is None:
        print("STOP: Enter a path to list VM")
        exit(1)
    path = None
    if args.path is None:
        path = 'Tenants-Internal'
        if args.product is not None:
            path += '/' + args.product
        if args.team is not None:
            path += '/' + args.team
        if args.folder is not None:
            path += '/' + args.folder
    else:
        path = args.path

    if args.disable_ssl_verification is None:
        SSLVerification = False
    else:
        SSLVerification = args.disable_ssl_verification

    if SSLVerification:
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE

    serviceInstance = SmartConnect(host=args.host, user=args.user,
                                   pwd=args.password, port=int(args.port),
                                   sslContext=sslContext)

    atexit.register(Disconnect, serviceInstance)
    content = serviceInstance.RetrieveContent()
    my_folder = find_folder(content, path)
    if my_folder is None:
        print ("Not a valid path. KILLING MYSELF")
        exit(1)
    vms = get_all_objs(content, [vim.VirtualMachine], folder=my_folder)
    for vm in vms:
        try:
            network = ['Information Can Not Be Obtained At the Moment']
            if vm.network is not None:
                network = []
                for net in vm.network:
                    network.append(net.name)
            freeSpace = vm.datastore[0].info.freeSpace
            capacity = vm.datastore[0].info.vmfs.capacity
            free_percent = str((float(freeSpace) / capacity) * 100) + ' %'
            print("""

Name: %s
UUID: %s
MemoryMB: %s
VM Network(s):
                """ % (vm.config.name, vm.config.instanceUuid,
                vm.config.hardware.memoryMB))
            for net in network:
                print("%s" % net)
            print("""
Powerstate: %s
Last Used: %s
Datastore:
    Name: %s
    Capacity: %s
    Free Space: %s
    Free Percentage: %s

                """ % (vm.runtime.powerState,
                vm.runtime.bootTime,
                vm.datastore[0].info.name,
                humanize.naturalsize(vm.datastore[0].info.vmfs.capacity, binary=True),
                humanize.naturalsize(vm.datastore[0].info.freeSpace, binary=True),
                free_percent))
        except Exception as error:
            print(error)
# Main section
if __name__ == "__main__":
    sys.exit(main())
