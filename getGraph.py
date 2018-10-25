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
channel = grpc.secure_channel('localhost:10009', ssl_creds)

# Creating a stub and requesting the client for the latest network graph
stub = lnrpc.LightningStub(channel)
request = ln.ChannelGraphRequest(include_unannounced=True)
response = stub.DescribeGraph(request, metadata=[('macaroon', macaroon)])

# Treat the response and build a multi line adjancency list from it
# https://networkx.github.io/documentation/stable/reference/readwrite/multiline_adjlist.html
adjListDic = defaultdict(list)

for edge in response.edges:
    # Build adj list from edges
    adjListDic[edge.node1_pub].append([edge.node2_pub, edge.capacity])
    adjListDic[edge.node2_pub].append([edge.node1_pub, edge.capacity])

# Write the adjlist file
f = open('lightningMLAdjList', 'w')
for (nodePubKey, adjList) in adjListDic.items():
    # Write the name of the node and the number of edges
    f.write(nodePubKey + " " + str(len(adjList)) + "\n")
    for adj in adjList:
        # Write the other node in the edge and the edge capacity
        f.write(adj[0] + " {'capacity':" + str(adj[1]/2) + "}\n")

f.close()

# Write a file with the correspondence between the nodes alias and pubkeys
f = open('nodeAlias.text', 'w')
for node in response.nodes:
    f.write(node.pub_key + " " + node.alias + "\n")

f.close()
