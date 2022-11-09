from streamlit_faker import get_streamlit_faker


def example():
    fake = get_streamlit_faker()
    fake.markdown()
    fake.markdown()
    fake.write()
    fake.selectbox()
    fake.slider()
    fake.altair_chart()


__func__ = get_streamlit_faker
__title__ = "Streamlit Faker"
__desc__ = "Fake Streamlit commands at the speed of light! Great for prototyping apps."
__icon__ = "🥷"
__examples__ = [example]
__author__ = "Arnaud Miribel"
__experimental_playground__ = False
