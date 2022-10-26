import streamlit as st
import  streamlit_vertical_slider

def example():
    vertical = vertical_slider(key="slider", 
                        default_value=25, 
                        step=1,
                        min_value=0, 
                        max_value=100,
                        track_color="gray",
                        thumb_color="blue",
                        slider_color="red"
                        )

__func__ = vertical_slider  # main function of your extra!
__title__ = "Vertical Slider"  # title of your extra!
__desc__ = "Continuos Vertical Slider with color customizations"  # description of your extra!
__icon__ = "🎚"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Carlos D. Serrano"
__pypi_name__ = "streamlit-vertical-slider"
__package_name__ = "streamlit_vertical_slider"
__github_repo__ = "sqlinsights/streamlit-vertical-slider" # Optional
__experimental_playground__ = False # Optional