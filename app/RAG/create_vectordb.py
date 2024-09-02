import chromadb
from typing import List
from embeddings import GeminiEmbeddingFunction
from langchain_chroma import Chroma


def create_chroma_db(documents: List, path: str, _name: str):
    """
    Creates a Chroma database using the provided documents, path, and collection name.

    Parameters:
    - documents: An iterable of documents to be added to the Chroma database.
    - path (str): The path where the Chroma database will be stored.
    - name (str): The name of the collection within the Chroma database.

    Returns:
    - Tuple[chromadb.Collection, str]: A tuple containing the created Chroma Collection and its name.
    """
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.create_collection(name=_name, embedding_function=GeminiEmbeddingFunction())

    for i, d in enumerate(documents):
        db.add(documents=d, ids=str(i))

    return db, _name

    # call this some where in your code
    # db,name =create_chroma_db(documents=chunkedtext,
    #                           path="C:\Repos\RAG\contents", #replace with your path
    #                           name="rag_experiment")


def load_chroma_collection(path, name):
    """
        Loads an existing Chroma collection from the specified path with the given name.

        Parameters:
        - path (str): The path where the Chroma database is stored.
        - name (str): The name of the collection within the Chroma database.

        Returns:
        - chromadb.Collection: The loaded Chroma Collection.
    """
    chroma_client = chromadb.PersistentClient(path=path)
    db = chroma_client.get_collection(name=name, embedding_function=GeminiEmbeddingFunction())

    return db


# db=load_chroma_collection(path="C:\Repos\RAG\contents", name="rag_experiment")


def create_langchain_chroma_db(documents: List, path: str, _name: str):
    persistent_client = chromadb.PersistentClient(path=path)
    collection = persistent_client.get_or_create_collection("collection_name")
    # collection.add(ids=["1", "2", "3"], documents=["a", "b", "c"])
    for i, d in enumerate(documents):
        collection.add(documents=d, ids=str(i))

    # using lanchain
    vector_store = Chroma(
        collection_name="collection_name",
        embedding_function=GeminiEmbeddingFunction,
        persist_directory="./chroma_langchain_db",  # Where to save data locally, remove if not neccesary
    )
    return vector_store, _name


def load_langchain_chroma_collection(path, collection_name, embeddings: GeminiEmbeddingFunction):
    persistent_client = chromadb.PersistentClient(path=path)
    collection = persistent_client.get_collection(collection_name=collection_name)
    vector_store_from_client = Chroma(
        client=persistent_client,
        collection_name="collection_name",
        embedding_function=embeddings,
    )

    return vector_store_from_client
