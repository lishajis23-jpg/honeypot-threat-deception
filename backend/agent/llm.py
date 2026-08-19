import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError("GEMINI_API_KEY not set")


client = genai.Client(api_key=api_key)


def generate_answer(question, context):

    prompt = f"""
You are the TechNova enterprise AI assistant.

Answer the user's question using the provided company context.

Use the retrieved context as the primary source of information.

If the answer cannot be found in the provided context, say:

"I don't have enough information in the company's knowledge base."

Do not invent company policies, employee information, procedures,
or other company-specific facts.

Company context:
{context}

User question:
{question}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":

    question = input("Enter a question: ")

    context = """
    This is a sample TechNova company policy.
    """

    answer = generate_answer(question, context)

    print("\nANSWER:")
    print(answer)