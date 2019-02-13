import codecs
import grpc
import os
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc
from collections import defaultdict

macaroon = codecs.encode(open('/home/joao/.lnd/data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open('/home/joao/.lnd/tls.cert', 'rb').read()
ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds, options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ])

# Creating a stub and requesting the client for the latest network graph
stub = lnrpc.LightningStub(channel)
request = ln.ChannelGraphRequest(include_unannounced=True)
response = stub.DescribeGraph(request, metadata=[('macaroon', macaroon)])

# Treat the response and build a multi line adjancency list from it
# https://networkx.github.io/documentation/stable/reference/readwrite/multiline_adjlist.html
adjListDic = defaultdict(list)

# Init adjList
for node in response.nodes:
    adjListDic[node.pub_key] = []

# Build adj list from edges
for edge in response.edges:
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
        adjListDic[edge.node1_pub].append([edge.node2_pub, edge.capacity])
        adjListDic[edge.node2_pub].append([edge.node1_pub, edge.capacity])


# Write the adjlist file
f = open('lightningAdjList.txt', 'w')
repeated = 0
for (nodePubKey, adjList) in adjListDic.items():
    # Write the name of the node and the number of edges
    f.write(nodePubKey + " " + str(len(adjList)) + "\n")
    for index, adj in enumerate(adjList):
        # Write the other node in the edge and the edge capacity
        f.write(adj[0] + " {'capacity':" + str(adj[1]/2) + "}\n")

f.close()

# Write a file with the correspondence between the nodes alias and pubkeys
f = open('nodeAlias.txt', 'w')
for node in response.nodes:
    f.write(node.pub_key + " " + node.alias + "\n")

f.close()
