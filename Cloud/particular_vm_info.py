#!/usr/bin/env python
import humanize
from pyVmomi import vim
import atexit
import argparse
import getpass
import ssl
from pyVim.connect import SmartConnect, Disconnect

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-host', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-port', '--port',
                        required=False,
                        action='store',
                        help="port to use, default 443", default=443)

    parser.add_argument('-user', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-password', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')

    parser.add_argument('-search_by', '--search_index',
                        required=True,
    					choices=['uuid','ip', 'vm_name'],
                        action='store',
                        help='Specify method of finding VM')

    parser.add_argument('-SSL', '--disable_ssl_verification',
                        required=False, type=bool,
                        action='store',
                        help='Disable ssl host certificate verification')

    parser.add_argument('-vm_name', '--name',
                        required=False,
                        action='store',
                        help='Enter the name of the VM')
    parser.add_argument('-uuid', '--uuid',
                        required=False,
                        action='store',
                        help='Enter the uuid of the VM')
    parser.add_argument('-product', '--product',
                        required=False,
                        action='store',
                        help='Enter the product you are working on - Integrity/Edge')
    parser.add_argument('-team', '--team',
                        required=False,
                        action='store',
                        help='Enter the team you are part of - "Team Avokado" on BPC')
    parser.add_argument('-ip_address', '--ip_address',
                        required=False,
                        action='store',
                        help='Enter the IP address of the VM')

    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    args = parser.parse_args()
    return args

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

def get_vm(content, vimtype, name, folder):
    objs = get_all_objs(content, vimtype, folder)
    for obj in objs:
        if obj.name == name:
            return obj
    return None

def main():
    global content, hosts, hostPgDict
    args = get_args()
    sslContext = None
    SSLVerification = False

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
    # doing this means you don't need to remember to disconnect your script/objects
    atexit.register(Disconnect, serviceInstance)

    vm_name = False
    vm_uuid = False
    vm_ip = False
    search_index = args.search_index
    if search_index == 'uuid':
        vm_uuid = True
    if search_index == 'ip':
        vm_ip = True
    if search_index == 'vm_name':
        vm_name = True

    search_index = serviceInstance.content.searchIndex
    folder = None
    if vm_name:
        if args.name is None:
            print("VM Name not provided. Please try again")
            exit(1)
        if args.product is None:
            print("Proper path not defined. Entire cloud will be searched")
        else:
            folder = 'Tenants-Internal/' + args.product
            if args.team is not None:
                folder += '/'+args.team
    if vm_name:
        my_folder = None
        if folder is not None:
            my_folder = find_folder(serviceInstance.content, folder)
            if my_folder is None:
                print ("Not a valid path. KILLING MYSELF")
                exit(1)
        vm = get_vm(serviceInstance.content, [vim.VirtualMachine], args.name, folder=my_folder)

    if vm_uuid:
        if args.uuid is None:
            print("UUID Not provided. Please try again")
            exit(1)
        try:
            vm = search_index.FindByUuid(None, args.uuid, True, True)
        except Exception as error:
            print("Error: %s" % error)
            exit(1)

    if vm_ip:
        if args.ip_address is None:
            print("IP address not provided. Please try again")
        try:
            vm = search_index.FindByIp(None, args.ip_address, True)
        except Exception as error:
            print("Error: %s" % error)
            exit(1)

    if vm is None:
        if vm_name:
            print("Could not find virtual machine '{0}'".format(args.name))
            exit(1)
        if vm_uuid:
            print("Could not find virtual machine '{0}'".format(args.uuid))
            exit(1)
        if vm_ip:
            print("Could not find virtual machine '{0}'".format(args.ip_address))
            exit(1)

    freeSpace = vm.datastore[0].info.freeSpace
    capacity = vm.datastore[0].info.vmfs.capacity
    free_percent = str((float(freeSpace) / capacity) * 100) + ' %'

    print("Found Virtual Machine")
    details = {}
    details = {
                   'Name': vm.summary.config.name,
                   'UUID': vm.summary.config.instanceUuid,
                   'Path to VM': vm.summary.config.vmPathName,
                   'Guest OS': vm.summary.config.guestFullName,
                   'Host': vm.runtime.host.name,
                   'Last Booted On': vm.runtime.bootTime,
                   'Total Memory': (str(vm.summary.config.memorySizeMB) + ' MB'),
                   'Reserved CPU': (str(vm.summary.config.cpuReservation) + ' MHz'),
                   'Current Memory Usage': (str(vm.summary.quickStats.guestMemoryUsage) + ' MB'),
                   'Current CPU Usage': (str(vm.summary.quickStats.overallCpuUsage) + ' MHz'),
                   'Powerstate': vm.runtime.powerState,
                   'Datastore Name': vm.datastore[0].info.name,
                   'DS Capacity': humanize.naturalsize(vm.datastore[0].info.vmfs.capacity, binary=True),
                   'DS Free Space': humanize.naturalsize(vm.datastore[0].info.freeSpace, binary=True),
                   'DS Free Percentage': free_percent
               }
    for name, value in details.items():
        print("{0:{width}{base}}: {1}".format(name, value, width=25, base='s'))

if __name__ == "__main__":
    main()
