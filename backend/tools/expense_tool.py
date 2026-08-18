expense = [
    {
        "employee":"Rahul",
        "role":"Developer",
        "amount":5000,
        "status":"Pending"
    },
    {
        "employee":"Anjali",
        "role":"Designer",  
        "amount":4500,
        "status":"Approved"
    },
    {
        "employee":"Vikram",
        "role":"Manager",
        "amount":6000,
        "status":"Rejected"
    }
]
def expense_lookup(employee_name):
    for record in expense:
        if record["employee"].lower() == employee_name.lower():
            return record
    return {"error": "No expense record found for the given employee."}
    return results

if __name__ == "__main__":
    record = expense_lookup("Rahul")
    print(record)
