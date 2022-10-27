import streamlit as st
from streamlit_toggle import st_toggle_switch


def example():
    st.write("## Toggle Switch")
    st_toggle_switch(
        label="Enable Setting?",
        key="switch_1",
        default_value=False,
        label_after=False,
        inactive_color="#D3D3D3",  # optional
        active_color="#11567f",  # optional
        track_color="#29B5E8",  # optional
    )


__func__ = st_toggle_switch  # main function of your extra!
__title__ = "Toggle Switch"  # title of your extra!
__desc__ = (
    "On/Off Toggle Switch with color custimizations"  # description of your extra!
)
__icon__ = "🔛"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Carlos D. Serrano"
__pypi_name__ = "streamlit-toggle_switch"
__package_name__ = "streamlit_toggle"
__github_repo__ = "sqlinsights/streamlit-toggle-switch"  # Optional
__experimental_playground__ = False  # Optional
