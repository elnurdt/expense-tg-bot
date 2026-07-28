def analyze_expenses(expenses):
    categories = {}

    for expense in expenses:
        if expense['category'] not in categories:
            categories[expense['category']] = expense['amount']
        else:
            categories[expense['category']] += expense['amount']

    return categories        