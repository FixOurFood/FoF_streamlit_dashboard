import streamlit as st

def label_plus_slider(label, min_value, max_value, value=None, step=1, ratio=(5,5), key=None, help=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    slider = c2.slider(label, min_value, max_value, value, step, label_visibility="collapsed", key=key, help=help)
    return slider

def label_plus_multiselect(label, options, ratio=(5,5), key=None, help=None, format_func=None):
    c1, c2 = st.columns(ratio)
    c1.write(label)
    if format_func is None:
        multiselect = c2.multiselect(label, options, label_visibility="collapsed", key=key, help=help)
    else:
        multiselect = c2.multiselect(label, options, label_visibility="collapsed", key=key, help=help, format_func=format_func)

    return multiselect
