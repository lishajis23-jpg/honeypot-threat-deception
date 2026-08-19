import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

from agent.ingestion import load_documents
from agent.llm import generate_answer
from agent.embeddings import create_embeddings
from agent.chunking import create_chunks
model = SentenceTransformer("all-MiniLM-L6-v2")

documents = load_documents()

print("Number of documents:", len(documents))


all_chunks = []

for document in documents:

    chunks = create_chunks(document["text"])

    for chunk in chunks:

        all_chunks.append({
            "filename": document["filename"],
            "text": chunk
        })

print("Number of chunks:", len(all_chunks))

texts = [
    chunk["text"]
    for chunk in all_chunks
]

embeddings = model.encode(texts)

embeddings = np.array(embeddings).astype("float32")
print("Embeddings type:", type(embeddings))
print("Embeddings shape:", embeddings.shape)
print("Number of chunks:", len(all_chunks))
print("Number of texts:", len(texts))

dimension = embeddings.shape[1]


index = faiss.IndexFlatL2(dimension)


index.add(embeddings)

def search(query, k=3):

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding
    ).astype("float32")


    distances, indices = index.search(
        query_embedding,
        k
    )


    results = []


    for i in indices[0]:

        results.append(
            all_chunks[i]
        )


    return results

def ask_question(query):

    results = search(query)


    context = "\n\n".join(
        result["text"]
        for result in results
    )


    answer = generate_answer(
        query,
        context
    )


    return answer, results

if __name__ == "__main__":

    query = input("\nAsk a question: ")


    answer, results = ask_question(query)


    print("\n" + "=" * 50)
    print("RETRIEVED INFORMATION")
    print("=" * 50)


    for result in results:

        print(
            "\nFILE:",
            result["filename"]
        )

        print(
            result["text"]
        )


    print("\n" + "=" * 50)
    print("FINAL ANSWER")
    print("=" * 50)


    print(answer)