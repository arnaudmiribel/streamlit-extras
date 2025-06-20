from streamlit_theme import st_theme

from .. import extra

st_theme = extra(st_theme)


def example_1():
    import streamlit as st
    from streamlit_theme import st_theme

    theme = st_theme()
    st.write(theme)


def example_2():
    import streamlit as st
    from streamlit_theme import st_theme

    adjust = st.toggle("Make the CSS adjustment")

    st.write("Input:")
    st.code(
        f"""
        st.write("Lorem ipsum")
        st_theme(adjust={adjust})
        st.write("Lorem ipsum")
        """
    )

    st.write("Output:")
    st.write("Lorem ipsum")
    st_theme(adjust=adjust)
    st.write("Lorem ipsum")


__title__ = "Theme"
__desc__ = """A component that returns the active theme of the Streamlit app.

**Deprecation note: With Streamlit 1.46.0 you can now detect if the viewer is in light mode or dark
mode at runtime with st.context.theme.**
"""
__icon__ = "🌗"
__examples__ = [example_1, example_2]
__author__ = "Gabriel Tem Pass"
__pypi_name__ = "st-theme"
__package_name__ = "streamlit_theme"
__github_repo__ = "gabrieltempass/streamlit-theme"
__streamlit_cloud_url__ = "https://st-theme-1.streamlit.app"
__experimental_playground__ = False
__deprecated__ = True
