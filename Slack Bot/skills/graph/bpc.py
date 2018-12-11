from vsphere_info import *

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
                        required=False, type=bool,
                        action='store',
                        help='Disable ssl host certificate verification')
    parser.add_argument('-option', '--option',
    					required=True,
    					choices=['datastore','host'],
                        action='store',
                        help='Specify either datastore or host option for printing')
    parser.add_argument('-ds', '--datastore',
                        action='store',
                        help='Used to only fetch information related to specified datastore name')
    parser.add_argument('-hs', '--hostName',
                        action='store',
                        help='Used to only fetch information related to specified host name')
    args = parser.parse_args()
    return args

def main():
    args = GetArgs()
    sslContext = None

    sslContext = None
    SSLVerification = False

    if args.disable_ssl_verification is None:
        SSLVerification = False
    else:
        SSLVerification = args.disable_ssl_verification

    if SSLVerification:
        sslContext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sslContext.verify_mode = ssl.CERT_NONE

    printOption = args.option
    queryDataStore = args.datastore
    queryHost = args.hostName

    if queryDataStore is not None and printOption == "host":
    	print "Must specify option datastore if querying about a specific datastore item"
    	exit(1)

    if queryHost is not None and printOption == "datastore":
        print "Must specify option host if querying about a specific host item"
        exit(1)

    try:
        si = SmartConnect(host=args.host, user=args.user,
                          pwd=args.password, port=int(args.port),
                          sslContext=sslContext)
        atexit.register(Disconnect, si)
        content = si.RetrieveContent()

        for datacenter in content.rootFolder.childEntity:

            print "##################################################"
            print "##################################################"
            print "### datacenter : " + datacenter.name
            print "##################################################"

            if printOption == DATA_STORE:
            	if queryDataStore is not None:
            		printDataStoreItem(datacenter, queryDataStore)
            	else:
                	printDataStore(datacenter)

            if printOption == HOST:
                option = "all" if queryHost is None else queryHost    
                printHostInfo(datacenter, option)
            

    except vmodl.MethodFault as error:
        print "Caught vmodl fault : " + error.msg
        return -1
    return 0

if __name__ == "__main__":
    main()
