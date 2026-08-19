def create_chunks(text, chunk_size=500, chunk_overlap=100):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        chunks.append(chunk)

        start += chunk_size - chunk_overlap

    return chunks


if __name__ == "__main__":

    sample_text = """
    TechNova is a software company.
    Employees must follow company policies.
    Employees should protect company information.
    """

    chunks = create_chunks(sample_text)

    for i, chunk in enumerate(chunks):

        print(f"\nCHUNK {i + 1}:")
        print(chunk)