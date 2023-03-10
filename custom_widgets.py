import streamlit as st

def label_plus_slider(label, min, max, set=None, step=1, ratio=(5,5), key=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    slider = c2.slider(label, min, max, set, step, label_visibility="collapsed", key=key)
    return slider

def label_plus_multiselect(label, options, ratio=(5,5), key=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    multiselect = c2.multiselect(label, options, label_visibility="collapsed", key=key)
    return multiselect
