import spacy
import re
from datetime import date, timedelta # Added for date handling example

nlp = spacy.load("en_core_web_sm")

def parse_query(query_text):
    doc = nlp(query_text.lower())
    sql_query = None

    # --- Rule 1: Show all users ---
    if "show all users" in query_text.lower():
        sql_query = "SELECT id, name, email, registration_date FROM users;"

    # --- Rule 2: Count users ---
    elif "how many users" in query_text.lower() or "count users" in query_text.lower():
        sql_query = "SELECT COUNT(*) FROM users;"

    # --- Rule 3: Total sales ---
    elif "total sales" in query_text.lower() or "sum of all orders" in query_text.lower():
        sql_query = "SELECT SUM(quantity * price) FROM orders;"

    # --- Rule 4: List all products ---
    elif "list all products" in query_text.lower():
        sql_query = "SELECT DISTINCT product_name FROM orders;"

    # --- Rule 5: Orders for specific product ---
    elif "orders for" in query_text.lower():
        product_name = None
        for token in doc:
            if token.text == "for" and token.head.text == "orders":
                start_index = token.i + 1
                end_index = start_index
                for j in range(start_index, len(doc)):
                    if doc[j].pos_ in ("NOUN", "PROPN", "ADJ") or doc[j].dep_ == "compound":
                        end_index = j
                    else:
                        break
                product_name = " ".join([t.text for t in doc[start_index:end_index+1]]).strip()
                break
        if product_name:
            sql_query = f"SELECT * FROM orders WHERE product_name ILIKE '%{product_name}%';"

    # --- Rule 6: Users named specific person ---
    elif "users named" in query_text.lower():
        print(f"DEBUG: 'users named' rule triggered for '{query_text}'")
        name = None
        
        # Try spaCy NER first
        print(f"DEBUG: Entities found: {[ (ent.text, ent.label_) for ent in doc.ents ]}")
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text
                print(f"DEBUG: Found PERSON entity via NER: '{name}'")
                break
        
        # FALLBACK: If NER didn't find a person, try to extract the last word
        if not name:
            tokens = query_text.lower().split()
            try:
                named_idx = tokens.index("named")
                if named_idx + 1 < len(tokens):
                    name = tokens[named_idx + 1]
                    print(f"DEBUG: Fallback: Extracted name '{name}' after 'named'")
            except ValueError:
                pass 

        if name:
            sql_query = f"SELECT * FROM users WHERE name ILIKE '%{name}%';"
        else:
            print("DEBUG: No name extracted after 'users named'.")

    # --- Rule 7: Count orders by product name ---
    elif "count orders by product name" in query_text.lower():
        sql_query = "SELECT product_name, COUNT(*) FROM orders GROUP BY product_name;"

    # --- Rule 8: Show product names and quantities ---
    elif "show product names and quantities" in query_text.lower() or \
         "list product names and quantities" in query_text.lower():
        sql_query = "SELECT product_name, quantity FROM orders;"

    # --- Rule 9: Orders by price greater than ---
    elif "orders by price greater than" in query_text.lower():
        price_value = None
        for token in doc:
            if token.like_num:
                try:
                    price_value = float(token.text)
                    break
                except ValueError:
                    continue
        if price_value is not None:
            sql_query = f"SELECT * FROM orders WHERE price > {price_value};"

    # --- Rule 10: Show user names (list of names) ---
    elif "users name" in query_text.lower() or \
         "user names" in query_text.lower() or \
         "show user names" in query_text.lower():
        sql_query = "SELECT name FROM users;"

    # --- Rule 11: Users with specific email address (BROADENED) ---
    elif "users with email" in query_text.lower() or \
         "users whose email is" in query_text.lower() or \
         "find users email" in query_text.lower(): # Added common phrases
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, query_text)
        
        if match:
            email_address = match.group(0)
            sql_query = f"SELECT * FROM users WHERE email ILIKE '{email_address}';"
            print(f"DEBUG: Extracted email: {email_address}")
        else:
            print("DEBUG: No email address found in query for email rule.")

    # --- Rule 12: Users registered after a certain date (moved import to top) ---
    elif "users registered after" in query_text.lower():
        date_str = None
        for ent in doc.ents:
            if ent.label_ == "DATE":
                date_str = ent.text.strip()
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    sql_query = f"SELECT * FROM users WHERE registration_date > '{date_str}';"
                    break
        if sql_query is None:
            if "last year" in query_text.lower():
                today = date.today()
                last_year_start = date(today.year - 1, 1, 1)
                sql_query = f"SELECT * FROM users WHERE registration_date >= '{last_year_start.isoformat()}';"
            
    # --- Rule 13: Orders from a specific user (by name) ---
    elif "orders from" in query_text.lower() and "user" in query_text.lower():
        user_name = None
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                user_name = ent.text
                break
        
        if not user_name:
            tokens = query_text.lower().split()
            try:
                from_idx = tokens.index("from")
                if from_idx + 1 < len(tokens):
                    user_name = tokens[from_idx + 1]
            except ValueError:
                pass

        if user_name:
            sql_query = f"""
                SELECT u.name, o.product_name, o.quantity, o.price, o.order_date
                FROM users u
                JOIN orders o ON u.id = o.user_id
                WHERE u.name ILIKE '%{user_name}%';
            """
    
    # --- Rule 14: Show orders with specific quantity ---
    elif "orders with quantity" in query_text.lower():
        quantity_value = None
        for token in doc:
            if token.like_num:
                try:
                    quantity_value = int(token.text)
                    break
                except ValueError:
                    continue
        if quantity_value is not None:
            sql_query = f"SELECT * FROM orders WHERE quantity = {quantity_value};"

    # --- Rule 15: All users registered in a specific year ---
    elif "all users registered in" in query_text.lower():
        year = None
        for token in doc:
            if token.like_num and len(token.text) == 4 and token.text.isdigit(): # Check for 4-digit number
                year = token.text
                break
        if year:
            sql_query = f"SELECT * FROM users WHERE EXTRACT(YEAR FROM registration_date) = {year};"


    print(f"Parsed query: '{query_text}' -> SQL: {sql_query}")
    return sql_query

# if __name__ == '__main__':
#     print("\n--- Running nlp_parser.py tests ---")
#     print(parse_query("Show all users"))
#     print(parse_query("How many users are there?"))
#     print(parse_query("What is the total sales amount?"))
#     print(parse_query("List all products"))
#     print(parse_query("Show orders for laptop"))
#     print(parse_query("Find users named Alice"))
#     print(parse_query("Find users named Bob Johnson"))
#     print(parse_query("Count orders by product name"))
#     print(parse_query("Show product names and quantities"))
#     print(parse_query("Orders by price greater than 100"))
#     print(parse_query("users name"))
#     print(parse_query("user names"))
#     print(parse_query("show user names"))
#     print(parse_query("users registered after 2023-04-01"))
#     print(parse_query("orders from user Alice Smith"))
#     print(parse_query("show orders with quantity 1"))
#     print(parse_query("users with email alice@example.com"))
#     print(parse_query("Find users whose email is bob@example.com")) # <-- NEW TEST CASE
#     print(parse_query("all users registered in 2023"))