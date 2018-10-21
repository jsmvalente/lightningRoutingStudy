import codecs
import grpc
import os
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

macaroon = codecs.encode(open('~/.lnd/data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open('~/.lnd/tls.cert', 'rb').read()
ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds)

# Creating a stub and requesting the client for the latest network graph
stub = lnrpc.LightningStub(channel)
request = ln.ChannelGraphRequest(include_unannounced=True)
response = stub.DescribeGraph(request, metadata=[('macaroon'), macaroon])
print(response)
