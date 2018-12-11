from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl

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


def main():
    sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    sslContext.verify_mode = ssl.CERT_NONE

    serviceInstance = SmartConnect(host='vcenter.bluecatlabs.net', user='mohaimen.khan@bluecatlabs.net',
                                   pwd='*****', port=443,
                                   sslContext=sslContext)

    content = serviceInstance.RetrieveContent()
    my_folder = find_folder(content, 'Tenants-Internal/Integrity/Team Avokado/Mohaimen')
    obj = get_all_objs(content, [vim.VirtualMachine], folder=my_folder)

    for vm in obj:
        print vm.config.name


# Main section
if __name__ == "__main__":
    exit(main())
