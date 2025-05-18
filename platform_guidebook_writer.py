import streamlit as st
import os

def run():
    st.title("📘 Platform Guidebook Generator")

    st.markdown("This tool reads your .py files and auto-generates documentation.")

    tools = [f for f in os.listdir() if f.endswith(".py") and f != "platform_guidebook_writer.py"]

    st.markdown("### Detected Modules:")
    for tool in sorted(tools):
        st.markdown(f"- `{tool}`")

    st.markdown("### Guidebook Snippet Example:")
    for tool in sorted(tools):
        display_name = tool.replace("_", " ").replace(".py", "").title()
        st.markdown(f"#### {display_name}")
        st.markdown(f"""
**Filename:** `{tool}`  
**Type:** Functional Module  
**Description:** This tool is part of your Venture North platform.  

> *This section can be expanded with:*
> - Setup steps  
> - Role-based access  
> - Where to find it in the sidebar  
""")