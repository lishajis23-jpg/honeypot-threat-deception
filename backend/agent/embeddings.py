from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(texts):

    embeddings = model.encode(texts)

    return embeddings


if __name__ == "__main__":

    texts = [
        "Employees receive paid leave.",
        "Employees must follow security policies.",
        "Employees can submit expense claims."
    ]

    embeddings = create_embeddings(texts)

    print("Number of texts:", len(texts))
    print("Embedding shape:", embeddings.shape)