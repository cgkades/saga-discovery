from twisted.internet import protocol, reactor, task
from twisted.protocols.basic import LineReceiver
import saganode


class Echo(protocol.Protocol):
    def dataReceived(self, data):
        line = data.lower().rstrip("\n")
        if line[:-1] == 'hello':
            self.handle_Hello(data)
        else:
            self.transport.write(data)

    def handle_Hello(self,data):
        self.transport.write("Hello back!\n")

class SagaNodeFactory(protocol.Factory):
    def buildProtocol(self, addr):
        return Echo()

def saga_node_run():
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



reactor.listenTCP(9909, SagaNodeFactory())
cm = task.LoopingCall(saga_node_run)
cm.start(5)
reactor.run()
