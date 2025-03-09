import streamlit as st
from streamlit_toggle import st_toggle_switch

from .. import extra

st_toggle_switch = extra(st_toggle_switch)


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


__title__ = "Toggle Switch"  # title of your extra!
__desc__ = """On/Off Toggle Switch with color customizations.
    **Note:** [st.toggle](https://docs.streamlit.io/library/api-reference/widgets/st.toggle) has been released in Streamlit 1.26.0!"""
__icon__ = "🔛"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Carlos D. Serrano"
__pypi_name__ = "streamlit-toggle-switch"
__package_name__ = "streamlit_toggle"
__github_repo__ = "sqlinsights/streamlit-toggle-switch"  # Optional
__forum_url__ = "https://discuss.streamlit.io/t/streamlit-toggle-switch/32474"
__playground__ = True
__deprecated__ = True
