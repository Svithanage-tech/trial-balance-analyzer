import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
import numpy as np

# Sample user data (replace this with a database or another authentication method in production)
names = ['User1', 'User2']  # User names
usernames = ['user1', 'user2']  # Usernames
passwords = ['password1', 'password2']  # Passwords (use hashed passwords in real-world)

# Create an authenticator object
authenticator = stauth.Authenticate(names, usernames, passwords, cookie_name="app_cookie", key="some_secret_key")

# Login section
name, authentication_status = authenticator.login("Login", "main")

# Simple variance calculation data (You can replace this with actual data)
variances = {
    'Account1': 15,  # 15% variance
    'Account2': 35,  # 35% variance
    'Account3': 25,  # 25% variance
}

# Handle user login and display based on subscription
if authentication_status:
    st.write(f"Hello {name}!")
    
    # Define the user subscription model (you can replace this with a real database or API)
    if name == 'User1':
        # User 1 is free and only has access to variances above 30%
        user_plan = 'free'
        st.write("You have free access.")
        st.write("You can view variances above 30%.")
        
    elif name == 'User2':
        # User 2 is a paid user and has access to variances above 10%
        user_plan = 'paid'
        st.write("You have premium access.")
        st.write("You can view variances above 10%.")
    
    # Display variances based on the user's subscription plan
    if user_plan == 'free':
        st.write("Viewing variances above 30%:")
        for account, variance in variances.items():
            if variance >= 30:
                st.write(f"{account}: {variance}%")
                
    elif user_plan == 'paid':
        st.write("Viewing variances above 10%:")
        for account, variance in variances.items():
            if variance >= 10:
                st.write(f"{account}: {variance}%")
                
else:
    st.warning("Please log in to access the app.")
