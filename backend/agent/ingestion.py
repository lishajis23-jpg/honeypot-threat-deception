from pathlib import Path
import os
def load_documents():

    # Get the folder where ingestion.py is located
    base_path = Path(__file__).parent

    # Documents folder is inside backend/agent
    documents_path = base_path / "documents"

    documents = []

    for file in documents_path.glob("*.txt"):

        text = file.read_text(encoding="utf-8")

        documents.append({
            "filename": file.name,
            "text": text
        })

    return documents


if __name__ == "__main__":

    documents = load_documents()

    print("Number of documents:", len(documents))

    for document in documents:

        print("\nFILE:", document["filename"])
        print(document["text"])