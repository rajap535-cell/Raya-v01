from pymongo import MongoClient

client = MongoClient("mongodb+srv://rajap535:vO7uZtx4A9TVoMeE@cluster0.vnfaxqc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client['Raya_database']
collection = db['conversation']

collection.insert_one({"test": "This is a test entry"})
print("Inserted test entry")
