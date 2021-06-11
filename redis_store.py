import redis
import pickle

r = redis.StrictRedis(host='localhost', port=6379, db=1)


def set(value, key='assets'):
    pickled_value = pickle.dumps(value)
    r.set(key, pickled_value)


def get(key='assets'):
    value = r.get(key)
    if not value:
        return []

    return pickle.loads(value)
