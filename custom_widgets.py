import streamlit as st

def label_plus_slider(label, min, max, set, ratio=(5,5)):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    slider = c2.slider(label, min, max, set, label_visibility="collapsed")
    return slider

def label_plus_multiselect(label, options, ratio=(5,5)):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    multiselect = c2.multiselect(label, options, label_visibility="collapsed")
    return multiselect
