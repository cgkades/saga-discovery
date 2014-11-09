import saganode
from twisted.internet import reactor
from twisted.application import service

class SagaNodeService(service.Service):
    def __init__(self, portNum):
        self.portNum = portNum

    def startService(self):
        self.saga_node_run()

    def stopService(self):
        pass

    def saga_node_run(self):
        '''Run the saga agent part
        This will register a saga node object and do the DHCP stuff
        '''
        node = saganode.SagaNode()
        print "Running initalization, this may take a while..."
        node.initalize()
        discovery_server = node.discovery_server
        parser.add_argument("-s","--server",help="Discovery server to use",default=discovery_server)
        args = parser.parse_args()
        if args.server:
            discovery_server = args.server

        if not discovery_server:
            print "No discovery server found in boot arguments or program arguments."
            # Need to insert logging here
        node.discovery_server = discovery_server

        if not node.is_dhcp_lease_valid():
            node.renew_dhcp_lease()
        node.post_data()
