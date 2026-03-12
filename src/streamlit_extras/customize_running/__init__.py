import time

import streamlit as st

from .. import extra

center_css = """
<style>

div[class*="StatusWidget"]{

    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 50%;
}

</style>
"""


@extra
def center_running():
    """
    Have the "running man" animation in the center of the screen instead of the top right corner.
    """
    st.html(center_css)


def example():
    click = st.button("Observe where the 🏃‍♂️ running widget is now!")
    if click:
        center_running()
        time.sleep(2)


__title__ = "Customize running"
__desc__ = "Customize the running widget"
__icon__ = "🏃‍♂️"
__examples__ = [example]
__author__ = "koninhoo"
__forum_url__ = "https://discuss.streamlit.io/t/change-the-running-widget-position/30466"
__playground__ = False
