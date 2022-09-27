import time

import streamlit as st


def center_running_toggle():

    hide_streamlit_style = """
            <style>

            div[class='css-4z1n4l ehezqtx5']{
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            border-radius: 15px;
            height: 40px;
            max-width: 160px;


            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50%;
            }

            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def example():
    click = st.button("Observe where the 🏃‍♂️ running widget is now!")
    if click:
        center_running_toggle()
        time.sleep(2)


__func__ = center_running_toggle
__title__ = "Running toggle"
__desc__ = "Change the position of the running widget"
__icon__ = "🏃‍♂️"
__examples__ = [example]
__author__ = "koninhoo"
__forum_url__ = (
    "https://discuss.streamlit.io/t/change-the-running-widget-position/30466"
)
__experimental_playground__ = False
