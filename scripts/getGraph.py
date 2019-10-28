import codecs
import grpc
import os
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
import numpy as np
from collections import defaultdict

macaroon = codecs.encode(open('/home/joao/.lnd/data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open('/home/joao/.lnd/tls.cert', 'rb').read()
ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds, options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ])

# Creating a stub and requesting the client for the latest network graph and graph info
stub = lnrpc.LightningStub(channel)
graphRequest = ln.ChannelGraphRequest(include_unannounced=True)
networkInfoRequest = ln.NetworkInfoRequest()
infoRequest = ln.request = ln.GetInfoRequest()
graphResponse = stub.DescribeGraph(graphRequest, metadata=[('macaroon', macaroon)])
networkInfoResponse = stub.GetNetworkInfo(networkInfoRequest, metadata=[('macaroon', macaroon)])
infoResponse = stub.GetInfo(infoRequest, metadata=[('macaroon', macaroon)])

# GetNetworkInfo returns some basic stats about the known channel graph from the point of view of the node.
print("Network Info: \n\n" + str(networkInfoResponse))

# GetInfo returns general information concerning the lightning node including
# it's identity pubkey, alias, the chains it is connected to, and information concerning the number of open+pending channels.
print("Info: \n\n" + str(infoResponse))

# Treat the response and build a multi line adjancency list from it
# https://networkx.github.io/documentation/stable/reference/readwrite/multiline_adjlist.html
adjListDic = defaultdict(list)

# Init adjList
for node in graphResponse.nodes:
    adjListDic[node.pub_key] = []

# Build adj list from edges
for edge in graphResponse.edges:

    # Find block in which the funding transaction associated with this channel is present,
    # this are the first 3 bytes of edge.channel_id
    # https://api.lightning.community/#channeledge
    uchannel_id = np.uint64(edge.channel_id)

    # Convert to hex and add padding to 16 bytes
    channel_idHex = hex(uchannel_id)
    channel_idHexPadd = '0x' + channel_idHex[2:].zfill(16)
    blockHeightHex = channel_idHexPadd[:8]
    blockHeight = int(blockHeightHex, 16)

    # Find if this edge already exists
    if any(adj[0] == edge.node2_pub for adj in adjListDic[edge.node1_pub]):
        # If it exists we add to that already existing capacity for both directions
        for (index, adj) in enumerate(adjListDic[edge.node1_pub]):
            if adj[0] == edge.node2_pub:
                adjListDic[edge.node1_pub][index][1] += edge.capacity
                break
        for (index, adj) in enumerate(adjListDic[edge.node2_pub]):
            if adj[0] == edge.node1_pub:
                adjListDic[edge.node2_pub][index][1] += edge.capacity
                break
    # IF it doesn't exist we add a new adjacency
    else:
        adjListDic[edge.node1_pub].append([edge.node2_pub, edge.capacity, blockHeight])
        adjListDic[edge.node2_pub].append([edge.node1_pub, edge.capacity, blockHeight])


# Write the adjlist file
f = open('adjList.txt', 'w')
for (nodePubKey, adjList) in adjListDic.items():
    # Write the name of the node and the number of edges
    f.write(nodePubKey + " " + str(len(adjList)) + "\n")
    for index, adj in enumerate(adjList):
        # Write the other node in the edge and the edge capacity
        f.write(adj[0] + " {'capacity':" + str(adj[1]) + ", 'funding_block':" + str(adj[2]) + "}\n")

f.close()

# Write a file with the correspondence between the nodes alias and pubkeys
f = open('nodeAlias.txt', 'w')
for node in graphResponse.nodes:
    f.write(node.pub_key + " " + (node.alias).encode('ascii', 'ignore').decode('ascii') + "\n")

f.close()

print("Saved " + str(len(graphResponse.nodes)) + " nodes and " + str(len(graphResponse.edges)) + " edges.")
