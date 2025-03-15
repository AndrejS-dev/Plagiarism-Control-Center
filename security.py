import hashlib
import streamlit as st

hashed_password = "b8ea7b7963a0fa7baaf4d71f4f0dc75a42aa7e4e1f3a406c809ca5b16ac7e9ab"
hashed_api_keys = "28366bffef0e8d0c92bbbf9943bf4dc9e66488a11b7db1e6a50f6a5b239aab34"

def hash_input(input_text):
    return hashlib.sha256(input_text.encode()).hexdigest()

def check_password(input_password):
    return hash_input(input_password) == hashed_password

def check_api_key(input_api_key):
    hashed = hash_input(input_api_key)
    return hashed == hashed_api_keys
