import pymongo 


def mongo_connect():
    try:
        client = pymongo.MongoClient(serverSelectionTimeoutMS=100)
        info = client.server_info()
        print(f"Connected - MongoDBv{info['version']}")
        return client
    except:
        print("Couldn't connect to MongoDB . . .")
        return None
    

