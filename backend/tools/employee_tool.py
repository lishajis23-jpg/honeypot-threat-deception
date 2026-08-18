employees = [
    {
        "name":"Rahul",
        "department":"engineering",
        "role":"software engineer"
    },
    {
        "name":"Priya",
        "department":"Human resources",
        "role":"HR manager"
    },
    {
        "name":"Arjun",
        "department":"Finance",
        "role":"Financial Analyst"
    }
]

def employee_search(name):
    for employee in employees:
        if employee["name"].lower() == name.lower():
            return employee

    return 
{
    "error":"Employee not found"
}

if __name__ == "__main__":
    result = employee_search("Rahul")
    print(result)