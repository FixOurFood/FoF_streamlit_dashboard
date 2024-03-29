import streamlit as st

def label_plus_slider(label, min_value, max_value, value=None, step=1, ratio=(5,5), key=None, help=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    slider = c2.slider(label, min_value, max_value, value, step, label_visibility="collapsed", key=key, help=help)
    return slider

def label_plus_multiselect(label, options, ratio=(5,5), key=None, help=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    multiselect = c2.multiselect(label, options, label_visibility="collapsed", key=key, help=help)
    return multiselect
