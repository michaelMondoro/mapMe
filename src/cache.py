import subprocess, time
import redis 

class Cache:
    def __init__(self):
        self._start_redis()
        self.started = True 
        try:
            self.redis = redis.Redis(host='localhost', port=6379, db=0) 
            self.redis.ping()
        except:
            print("Redis cache is not available!")
            exit(1)

    def _start_redis(self):
        print("starting redis cache . . .")
        subprocess.Popen(['redis-server'])
        time.sleep(2)

    def get(self, key):
        value = self.redis.get(key)
        if value:
            return value.decode() 
        else:
            return None
    
    def set(self, key, value):
        self.redis.set(key, value)

