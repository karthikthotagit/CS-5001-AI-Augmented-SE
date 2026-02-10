import re
import streamlit as st

def validate_email(email: str) -> bool:
    """
    Validates an email address using a simple regex pattern.

    Args:
        email: The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def main():
    """
    Main function to run the Streamlit app for email validation.
    """
    st.title("Email Validator")
    email = st.text_input("Enter your email address:")
    if st.button("Validate"):
        if validate_email(email):
            st.success("Valid email address!")
        else:
            st.error("Invalid email address!")

if __name__ == "__main__":
    main()
