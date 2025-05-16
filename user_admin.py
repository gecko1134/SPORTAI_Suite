
import streamlit as st
import json
import os

def run():
    st.title("👤 Admin: User Management")

    if not os.path.exists("users.json"):
        st.error("users.json file not found.")
        return

    with open("users.json", "r") as f:
        users = json.load(f)

    st.subheader("Add New User")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role", ["admin", "board", "sponsor", "member"])
    if st.button("Add User"):
        if email in users:
            st.warning("User already exists.")
        else:
            users[email] = {"password": password, "role": role}
            with open("users.json", "w") as f:
                json.dump(users, f, indent=2)
            st.success("User added.")

    st.subheader("Existing Users")
    for email, data in users.items():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write(email)
        with col2:
            new_role = st.selectbox(f"Role for {email}", ["admin", "board", "sponsor", "member"], index=["admin", "board", "sponsor", "member"].index(data["role"]))
            if new_role != data["role"]:
                users[email]["role"] = new_role
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=2)
        with col3:
            if st.button(f"Delete {email}"):
                del users[email]
                with open("users.json", "w") as f:
                    json.dump(users, f, indent=2)
                st.experimental_rerun()
