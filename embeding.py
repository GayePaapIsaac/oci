from qdrant_client import QdrantClient
import json


client = QdrantClient(host="localhost", port=6333)

collection_name = "Corpus_V14"



# Charger le contenu du fichier JSON
with open("data_chunk.json", "r", encoding="utf-8") as f:
    content = json.load(f)


documents = [doc["context"] for doc in content]
metadata = [doc["metadata"] for doc in content]
  
        
client.add(
    collection_name=collection_name,
    documents=documents,
    metadata=metadata,
)


print("Les documents ont été ajoutés avec succès à la collection.")