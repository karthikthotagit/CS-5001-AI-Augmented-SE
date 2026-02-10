def process_credit_card_info(name: str, card_number: str, expiry_date: str, cvv: str) -> str:
    """
    Process credit card information and return a confirmation message.
    """
    # Basic validation
    if not all([name, card_number, expiry_date, cvv]):
        return "All fields are required."
    
    if len(card_number) != 16 or not card_number.isdigit():
        return "Invalid card number. Must be 16 digits."
    
    if len(cvv) != 3 or not cvv.isdigit():
        return "Invalid CVV. Must be 3 digits."
    
    return f"Credit card information for {name} processed successfully!"
