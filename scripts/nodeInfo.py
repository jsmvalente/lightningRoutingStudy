import codecs
import grpc
import os
import rpc_pb2 as ln
import rpc_pb2_grpc as lnrpc

macaroon = codecs.encode(open('/home/joao/.lnd/data/chain/bitcoin/mainnet/admin.macaroon', 'rb').read(), 'hex')
os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
cert = open('/home/joao/.lnd/tls.cert', 'rb').read()
ssl_creds = grpc.ssl_channel_credentials(cert)
channel = grpc.secure_channel('localhost:10009', ssl_creds, options=[
        ('grpc.max_send_message_length', 50 * 1024 * 1024),
        ('grpc.max_receive_message_length', 50 * 1024 * 1024)
        ])

stub = lnrpc.LightningStub(channel)
request = ln.GetInfoRequest()
response = stub.GetInfo(request, metadata=[('macaroon', macaroon)])
print(response)
