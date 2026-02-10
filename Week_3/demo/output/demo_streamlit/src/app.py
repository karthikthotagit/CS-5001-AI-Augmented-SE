import streamlit as st
from src.services.credit_card_service import process_credit_card_info

def main():
    st.title("Credit Card System")
    
    with st.form("credit_card_form"):
        name = st.text_input("Cardholder Name")
        card_number = st.text_input("Card Number")
        expiry_date = st.text_input("Expiry Date (MM/YY)")
        cvv = st.text_input("CVV")
        
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            result = process_credit_card_info(name, card_number, expiry_date, cvv)
            st.success(result)

if __name__ == "__main__":
    main()
