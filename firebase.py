import streamlit as st
from replit import auth  # Import the replit authentication module

# Streamlit App
def app():
    st.set_page_config(page_title="Login | FERN", page_icon="🔒", layout="centered")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔑 Welcome to FERN")
        auth_choice = st.radio("Select an option", ["Login", "Sign Up"])

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if auth_choice == "Sign Up":
            username = st.text_input("Choose a Username")
            if st.button("Create Account"):
                try:
                    user = auth.sign_up(email=email, password=password)
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                    st.session_state["email"] = email
                    st.success("Account created successfully! Please log in.")
                except Exception as e:
                    st.error(f"Sign-up failed: {e}")
        else:
            if st.button("Login"):
                try:
                    user = auth.sign_in(email=email, password=password)
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = user["email"]
                    st.session_state["email"] = email
                    st.success("Logged in successfully!")
                except Exception as e:
                    st.error(f"Login failed: {e}")
            
        if st.button("Forgot Password?"):
            # Implement password reset here if needed
            pass
    else:
        st.write(f"✅ Logged in as {st.session_state['username']} ({st.session_state['email']})")
        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    app()
