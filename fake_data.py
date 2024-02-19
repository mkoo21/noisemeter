from questdb.ingress import Sender, IngressError, TimestampNanos
import os
import sys
import random
import time

HOST = os.getenv('QDB_CLIENT_HOST', 'localhost')
PORT = os.getenv('QDB_CLIENT_PORT', 9009)
TLS = os.getenv('QDB_CLIENT_TLS', "False" ).lower() in ('true', '1', 't')
AUTH_KID = os.getenv('QDB_CLIENT_AUTH_KID', '')
AUTH_D = os.getenv('QDB_CLIENT_AUTH_D', '')
AUTH_X = os.getenv('QDB_CLIENT_AUTH_X', '')
AUTH_Y = os.getenv('QDB_CLIENT_AUTH_Y', '')

DEVICE_TYPES = ["blue", "red", "green", "yellow"]
ITER = 10000
BATCH = 100
DELAY = 0.5
MIN_LAT = 43.6377600732075
MAX_LAT = 43.834312228067525
MIN_LON = -79.55020432158423
MAX_LON = -79.10777702129245


def send(host: str = HOST, port: int = PORT):
    try:
        auth = None
        if AUTH_KID and AUTH_D and AUTH_X and AUTH_Y:
            sys.stdout.write(f'Ingestion using credentials\n')
            auth = ( AUTH_KID, AUTH_D, AUTH_X, AUTH_Y )
        with Sender(host, port, auth=auth, tls=TLS) as sender:
            for it in range(ITER):
                for i in range(BATCH):
                    sender.row(
                        'ingress_test',
                        symbols={'device_type': random.choice(DEVICE_TYPES)},
                        columns={
                            "lat": random.uniform(MIN_LAT, MAX_LAT),
                            "lon": random.uniform(MIN_LON, MAX_LON),
                            "decibels": random.randint(0.0, 200.0),
                            "version": 0.1,
                        },
                        at=TimestampNanos.now())
                sys.stdout.write(f'sent : {BATCH} rows\n')
                sender.flush()
                time.sleep(DELAY)
    except IngressError as e:
        sys.stderr.write(f'Got error: {e}')


if __name__ == '__main__':
    sys.stdout.write(f'Ingestion started. Connecting to {HOST} {PORT}\n')
    send()
