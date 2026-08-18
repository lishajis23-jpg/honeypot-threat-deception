from agent.retriever import search

def knowledge_search(query):
    results = search(query)

    if not results:
        return 
        {
            "error":"no relevant information found in the knowledge base"
        }
    return [
        {
            "filename": result["filename"],
            "content": result["content"]
        }
        for result in results
    ]    

if __name__ == "__main__":
    results = knowledge_search(
        "what is the leave policy?"
    )
    print(result)