from retry import retry
from binascii import hexlify, unhexlify
import pickle
import zlib
import io
import os
import boto3
import botocore

import sqlite3

class Cache:
    def __init__(self):
        pass

    def put(self, key, obj):
        pass

    def get(self, key):
        return None

    def has(self, key):
        return False

    def delete(self, key):
        pass

    def serialize(self, obj):
        pickled = pickle.dumps(obj)
        compressed = self.compress(pickled)
        return compressed

    def deserialize(self, data):
        pickled = self.decompress(data)
        obj = pickle.loads(pickled)
        return obj

    def compress(self, data):
        return zlib.compress(data)

    def decompress(self, data):
        return zlib.decompress(data)

    def encode(self, name):
        return hexlify(name.encode('utf8')).decode('utf8')

    def decode(self, name):
        return unhexlify(name).decode('utf8')

    def call(self, key, fun, *a, **kw):
        if self.has(key):
            return self.get(key)
        else:
            resp = fun(*a, **kw)
            self.put(key, resp)
            return resp


class DiskCache(Cache):
    def __init__(self, root):
        super().__init__()
        self.root = root

    def path(self, key):
        return os.path.join(self.root, self.encode(key))

    def put(self, key, obj):
        path = self.path(key)
        data = self.serialize(obj)
        with open(path, 'wb') as f:
            f.write(data)

    def get(self, key):
        path = self.path(key)
        with open(path, 'rb') as f:
            data = f.read()
        obj = self.deserialize(data)
        return obj

    def has(self, key):
        path = self.path(key)
        return os.path.exists(path)

    def delete(self, key):
        path = self.path(key)
        os.remove(path)


class S3Cache(Cache):

    def __init__(self, **kw):
        super().__init__()
        bucket = kw.get('bucket') or os.getenv('S3_CACHE_BUCKET', 'ask-my-pdf')
        prefix = kw.get('prefix') or os.getenv('S3_CACHE_PREFIX', 'cache/x1')
        region = kw.get('region') or os.getenv('S3_REGION', 'sfo3')
        url = kw.get('url') or os.getenv('S3_URL', f'https://{region}.digitaloceanspaces.com')
        key = os.getenv('S3_KEY', '')
        secret = os.getenv('S3_SECRET', '')
        #
        if not key or not secret:
            raise Exception("No S3 credentials in environment variables!")
        #
        self.session = boto3.session.Session()
        self.s3 = self.session.client('s3',
                                      config=botocore.config.Config(s3={'addressing_style': 'virtual'}),
                                      region_name=region,
                                      endpoint_url=url,
                                      aws_access_key_id=key,
                                      aws_secret_access_key=secret,
                                      )
        self.bucket = bucket
        self.prefix = prefix

    def get_s3_key(self, key):
        return f'{self.prefix}/{key}'

    def put(self, key, obj):
        s3_key = self.get_s3_key(key)
        data = self.serialize(obj)
        f = io.BytesIO(data)
        self.s3.upload_fileobj(f, self.bucket, s3_key)

    def get(self, key, default=None):
        s3_key = self.get_s3_key(key)
        f = io.BytesIO()
        try:
            self.s3.download_fileobj(self.bucket, s3_key, f)
        except:
            f.close()
            return default
        f.seek(0)
        data = f.read()
        obj = self.deserialize(data)
        return obj

    def has(self, key):
        s3_key = self.get_s3_key(key)
        try:
            self.s3.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except:
            return False

    def delete(self, key):
        self.s3.delete_object(
            Bucket=self.bucket,
            Key=self.get_s3_key(key))


class ChromaCache(Cache):
    def __init__(self, **kw):
        super().__init__()
        # Initialize Chroma client
        # This is a placeholder; replace it with actual initialization code based on Chroma's API
        self.chroma = self.initialize_chroma_client(**kw)

    def initialize_chroma_client(self, **kw):
        # Initialize and return a Chroma client
        # This method should be replaced with actual code to connect to Chroma
        pass

    def put(self, key, obj):
        chroma_key = self.encode(key)
        data = self.serialize(obj)
        # Assuming Chroma's client has a method 'put' for storing data
        self.chroma.put(chroma_key, data)

    def get(self, key, default=None):
        chroma_key = self.encode(key)
        try:
            # Assuming Chroma's client has a method 'get' for retrieving data
            data = self.chroma.get(chroma_key)
            if data is None:
                return default
            obj = self.deserialize(data)
            return obj
        except Exception as e:
            # Handle exceptions, possibly logging them, and return default value
            print(f"Error accessing Chroma: {e}")
            return default

    def has(self, key):
        chroma_key = self.encode(key)
        try:
            # Assuming Chroma's client has a method to check if a key exists
            return self.chroma.has(chroma_key)
        except Exception as e:
            print(f"Error checking key in Chroma: {e}")
            return False

    def delete(self, key):
        chroma_key = self.encode(key)
        # Assuming Chroma's client has a method 'delete' for removing data
        self.chroma.delete(chroma_key)


class VectorDBCache(Cache):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.init_db()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                data BLOB
            )
        ''')
        self.conn.commit()

    def put(self, key, obj):
        data = self.serialize(obj)
        cursor = self.conn.cursor()
        cursor.execute('REPLACE INTO cache (key, data) VALUES (?, ?)', (key, data))
        self.conn.commit()

    def get(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM cache WHERE key = ?', (key,))
        row = cursor.fetchone()
        if row:
            return self.deserialize(row[0])
        return None

    def has(self, key):
        cursor = self.conn.cursor()
        cursor.execute('SELECT 1 FROM cache WHERE key = ?', (key,))
        return cursor.fetchone() is not None

    def delete(self, key):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM cache WHERE key = ?', (key,))
        self.conn.commit()


def get_cache(**kw):
    mode = os.getenv('CACHE_MODE', '').upper()
    path = os.getenv('CACHE_PATH', '')
    db_path = os.getenv('VECTOR_DB_PATH', 'vector_cache.db')
    if mode == 'DISK':
        return DiskCache(path)
    elif mode == 'S3':
        return S3Cache(**kw)
    elif mode == 'VECTOR_DB':
        return ChromaCache(db_path)
    else:
        return Cache()


if __name__ == "__main__":
    # cache = S3Cache()
    cache = DiskCache('../data/cache/')


    cache.put('xxx', {'a': 1, 'b': 22})
    print('get xxx', cache.get('xxx'))
    print('has xxx', cache.has('xxx'))
    print('has yyy', cache.has('yyy'))
    print('delete xxx', cache.delete('xxx'))
    print('has xxx', cache.has('xxx'))
    print('get xxx', cache.get('xxx'))
#
