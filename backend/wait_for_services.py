import os
import time
import sys

# Wait for Postgres
import psycopg2
try:
    import redis
    _HAVE_REDIS_PY = True
except Exception:
    _HAVE_REDIS_PY = False
import subprocess

DB_HOST = os.getenv('DATABASE_HOST', 'localhost')
DB_PORT = int(os.getenv('DATABASE_PORT', '5432'))
DB_NAME = os.getenv('DATABASE_NAME', 'DV3AdminDBDevGit')
DB_USER = os.getenv('DATABASE_USER', 'postgres')
DB_PASSWORD = os.getenv('DATABASE_PASSWORD', 'root')

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = 6379
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')

RETRIES = int(os.getenv('WAIT_RETRIES', '30'))
SLEEP = int(os.getenv('WAIT_SLEEP', '2'))

def wait_postgres():
    for i in range(RETRIES):
        try:
            conn = psycopg2.connect(host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD)
            conn.close()
            print('Postgres is available')
            return True
        except Exception as e:
            print(f'Postgres not ready ({i+1}/{RETRIES}):', e)
            time.sleep(SLEEP)
    return False

def wait_redis():
    for i in range(RETRIES):
        try:
            if _HAVE_REDIS_PY:
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, socket_connect_timeout=2)
                if r.ping():
                    print('Redis is available')
                    return True
            else:
                # fallback to redis-cli if python client not available
                cmd = ["redis-cli", "-h", REDIS_HOST, "-p", str(REDIS_PORT)]
                if REDIS_PASSWORD:
                    cmd += ["-a", REDIS_PASSWORD]
                cmd += ["ping"]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=3)
                if proc.returncode == 0 and proc.stdout.strip() == b"PONG":
                    print('Redis is available (via redis-cli)')
                    return True
        except Exception as e:
            print(f'Redis not ready ({i+1}/{RETRIES}):', e)
        time.sleep(SLEEP)
    return False

if __name__ == '__main__':
    ok = wait_postgres()
    if not ok:
        print('Postgres did not become available, exiting')
        sys.exit(1)
    ok = wait_redis()
    if not ok:
        print('Redis did not become available, exiting')
        sys.exit(1)
    print('All services are ready')
    sys.exit(0)
