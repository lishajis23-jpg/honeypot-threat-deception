from tools.knowledge_tool import knowledge_search
from tools.employee_tool import employee_search
from tools.expense_tool import expense_lookup

from google import genai
from google.genai import errors
from google.genai import types

from dotenv import load_dotenv
import os


# ==========================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not set")

client = genai.Client(api_key=api_key)


# ==========================================
# ALLOWED TOOLS
# ==========================================

ALLOWED_TOOLS = {
    "employee_search",
    "expense_lookup",
    "knowledge_search"
}


# ==========================================
# EMPLOYEE SEARCH TOOL
# ==========================================

employee_search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="employee_search",
            description=(
                "Search the TechNova employee database "
                "using an employee's name."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "name": types.Schema(
                        type="STRING",
                        description=(
                            "The name of the employee to search for."
                        )
                    )
                },
                required=["name"]
            )
        )
    ]
)


# ==========================================
# EXPENSE LOOKUP TOOL
# ==========================================

expense_lookup_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="expense_lookup",
            description=(
                "Look up expense records for a TechNova employee."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "employee_name": types.Schema(
                        type="STRING",
                        description="The name of the employee."
                    )
                },
                required=["employee_name"]
            )
        )
    ]
)


# ==========================================
# KNOWLEDGE / RAG TOOL
# ==========================================

knowledge_search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="knowledge_search",
            description=(
                "Search the TechNova company knowledge base "
                "for policies, procedures, rules, benefits, "
                "and other company documentation."
            ),
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "query": types.Schema(
                        type="STRING",
                        description=(
                            "The question or information to search "
                            "for in the company knowledge base."
                        )
                    )
                },
                required=["query"]
            )
        )
    ]
)


# ==========================================
# TOOL RESULT VALIDATION
# ==========================================

def validate_tool_result(tool_name, result):

    # Tool returned nothing
    if result is None:

        return {
            "success": False,
            "error": f"{tool_name} returned no result"
        }

    # Tool returned an error
    if isinstance(result, dict) and "error" in result:

        return {
            "success": False,
            "error": result["error"]
        }

    # Tool returned valid data
    return {
        "success": True,
        "data": result
    }


# ==========================================
# EXECUTE TOOL
# ==========================================

def execute_tool(tool_name, arguments):

    # --------------------------------------
    # SECURITY CHECK
    # --------------------------------------

    if tool_name not in ALLOWED_TOOLS:

        return {
            "error": "Tool is not authorized"
        }

    # --------------------------------------
    # EMPLOYEE SEARCH
    # --------------------------------------

    if tool_name == "employee_search":

        name = arguments.get("name")

        if not name:
            return {
                "error": "Employee name is required"
            }

        return employee_search(name)

    # --------------------------------------
    # EXPENSE LOOKUP
    # --------------------------------------

    elif tool_name == "expense_lookup":

        employee_name = arguments.get("employee_name")

        if not employee_name:
            return {
                "error": "Employee name is required"
            }

        return expense_lookup(employee_name)

    # --------------------------------------
    # KNOWLEDGE / RAG SEARCH
    # --------------------------------------

    elif tool_name == "knowledge_search":

        query = arguments.get("query")

        if not query:
            return {
                "error": "Knowledge search query is required"
            }

        return knowledge_search(query)

    # --------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------

    return {
        "error": "Unknown tool requested"
    }


# ==========================================
# AGENT
# ==========================================

def run_agent(user_query):

    # Conversation and tool history
    contents = [user_query]

    # Prevent infinite agent loops
    max_steps = 5

    for step in range(max_steps):

        print(f"\nAGENT STEP: {step + 1}")

        # ==================================
        # CALL GEMINI
        # ==================================

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[
                        employee_search_tool,
                        expense_lookup_tool,
                        knowledge_search_tool
                    ]
                )
            )

        except errors.ServerError:

            return (
                "The AI service is temporarily unavailable. "
                "Please try again."
            )

        # ==================================
        # CHECK RESPONSE
        # ==================================

        if not response.candidates:

            return "The AI service returned no response."

        # ==================================
        # CHECK FOR FUNCTION CALLS
        # ==================================

        function_calls = []

        for part in response.candidates[0].content.parts:

            if part.function_call:

                function_calls.append(part.function_call)

        # ==================================
        # NO TOOL NEEDED
        # ==================================

        if not function_calls:

            return response.text

        # ==================================
        # ADD GEMINI RESPONSE TO HISTORY
        # ==================================

        contents.append(
            response.candidates[0].content
        )

        # ==================================
        # EXECUTE FUNCTION CALLS
        # ==================================

        for function_call in function_calls:

            tool_name = function_call.name
            arguments = function_call.args

            print("\n==============================")
            print("TOOL REQUEST")
            print("==============================")

            print("Tool:", tool_name)
            print("Arguments:", arguments)

            # ==================================
            # EXECUTE TOOL
            # ==================================

            tool_result = execute_tool(
                tool_name,
                arguments
            )

            # ==================================
            # PRINT TOOL RESULT
            # ==================================

            print("\n==============================")
            print("TOOL RESULT")
            print("==============================")

            print(tool_result)

            # ==================================
            # VALIDATE TOOL RESULT
            # ==================================

            validated_result = validate_tool_result(
                tool_name,
                tool_result
            )

            print("\n==============================")
            print("VALIDATED RESULT")
            print("==============================")

            print(validated_result)

            # ==================================
            # SEND RESULT BACK TO GEMINI
            # ==================================

            tool_response = types.Part.from_function_response(
                name=tool_name,
                response=validated_result
            )

            contents.append(tool_response)

    # ==========================================
    # MAXIMUM STEPS REACHED
    # ==========================================

    return (
        "I was unable to complete the request "
        "within the allowed number of steps."
    )


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    query = input("Ask the TechNova agent: ")

    response = run_agent(query)

    print("\n==============================")
    print("MODEL RESPONSE")
    print("==============================")

    print(response)