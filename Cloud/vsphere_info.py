#!/usr/bin/env python

import pyVmomi
import argparse
import atexit
import itertools
import humanize
import ssl
from pyVmomi import vim, vmodl
from pyVim.connect import SmartConnect, Disconnect

MBFACTOR = float(1 << 20)

DATA_STORE='datastore'
HOST='host'

def printAllHostInfo(hostList):

    for host in hostList:
        try:
            summary = host.summary
            stats = summary.quickStats
            hardware = host.hardware
            cpuUsage = stats.overallCpuUsage
            memoryCapacity = hardware.memorySize
            memoryCapacityInMB = hardware.memorySize/MBFACTOR
            memoryUsage = stats.overallMemoryUsage
            freeMemoryPercentage = 100 - (
                (float(memoryUsage) / memoryCapacityInMB) * 100
            )
            print "--------------------------------------------------"
            print "Host name: ", host.name
            print "Host CPU usage: ", cpuUsage
            print "Host memory capacity: ", humanize.naturalsize(memoryCapacity,
                                                                 binary=True)
            print "Host memory usage: ", memoryUsage / 1024, "GB"
            print "Free memory percentage: " + str(freeMemoryPercentage) + "%"
            print "--------------------------------------------------"
        except Exception as error:
            print "Unable to access information for host: ", host.name
            print error
            pass

def printHostItem(hostList, name):
    for host in hostList:
        if host.name == name:
            try:
                summary = host.summary
                stats = summary.quickStats
                hardware = host.hardware
                cpuUsage = stats.overallCpuUsage
                memoryCapacity = hardware.memorySize
                memoryCapacityInMB = hardware.memorySize/MBFACTOR
                memoryUsage = stats.overallMemoryUsage
                freeMemoryPercentage = 100 - (
                    (float(memoryUsage) / memoryCapacityInMB) * 100
                )
                print "--------------------------------------------------"
                print "Host name: ", host.name
                print "Host CPU usage: ", cpuUsage
                print "Host memory capacity: ", humanize.naturalsize(memoryCapacity,
                                                                     binary=True)
                print "Host memory usage: ", memoryUsage / 1024, "GB"
                print "Free memory percentage: " + str(freeMemoryPercentage) + "%"
                print "--------------------------------------------------"
            except Exception as error:
                print "Unable to access information for host: ", host.name
                print error
                pass

def printComputeResourceInformation(computeResource,option):
    try:
        hostList = computeResource.host
        print "##################################################"
        print "Compute resource name: ", computeResource.name
        print "##################################################"

        if option == "all":
            printAllHostInfo(hostList)
        else:
            printHostItem(hostList,option)

    except Exception as error:
        print "Unable to access information for compute resource: ",
        computeResource.name
        print error
        pass

def printToScreen(name, capacity,uncommittedSpace,freeSpace,freeSpacePercentage):
    print "##################################################"
    print "Datastore name: ", name
    print "Capacity: ", humanize.naturalsize(capacity, binary=True)
    if uncommittedSpace is not None:
        provisionedSpace = (capacity - freeSpace) + uncommittedSpace
        print "Provisioned space: ", humanize.naturalsize(provisionedSpace,
                                                          binary=True)
    print "Free space: ", humanize.naturalsize(freeSpace, binary=True)
    print "Free space percentage: " + str(freeSpacePercentage) + "%"
    print "##################################################"

def printDatastoreInformation(datastore):
    try:
        summary = datastore.summary
        capacity = summary.capacity
        freeSpace = summary.freeSpace
        uncommittedSpace = summary.uncommitted
        freeSpacePercentage = (float(freeSpace) / capacity) * 100
        printToScreen(summary.name,capacity,freeSpace,uncommittedSpace,freeSpacePercentage)
    except Exception as error:
        print "Unable to access summary for datastore: ", datastore.name
        print error
        pass

def printDataStoreItem(datacenter, datastoreName):
    datastores = datacenter.datastore
    for ds in datastores:
        try:
            if ds.summary.name == datastoreName:
                summary = ds.summary
                capacity = summary.capacity
                freeSpace = summary.freeSpace
                uncommittedSpace = summary.uncommitted
                freeSpacePercentage = (float(freeSpace) / capacity) * 100
                printToScreen(summary.name,capacity,freeSpace,uncommittedSpace,freeSpacePercentage)
        except Exception as error:
            print "Unable to access summary for datastore: ", ds.name
            print error
            pass

def printDataStore(datacenter):
    datastores = datacenter.datastore
    for ds in datastores:
        printDatastoreInformation(ds)

def printHostInfo(datacenter, option):
    if hasattr(datacenter.vmFolder, 'childEntity'):
        hostFolder = datacenter.hostFolder
        computeResourceList = hostFolder.childEntity
        for computeResource in computeResourceList:
            printComputeResourceInformation(computeResource,option)
