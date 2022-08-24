import setuptools

VERSION = "0.0.2"

NAME = "streamlit_extras"

DESCRIPTION = "A library to discover, try, install and share Streamlit extras"

LONG_DESCRIPTION = """Streamlit Extras is a place for you to discover, try, install and share() Streamlit re-usable bits we call extras Head over to extras.streamlitapp.com to discover them and if you're seduced... go ahead and get started!"""

INSTALL_REQUIRES = [
    "streamlit==1.11.1",
    "htbuilder",
]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url="https://github.com/arnaudmiribel/streamlit-extras",
    project_urls={
        "Source": "https://github.com/arnaudmiribel/streamlit-extras",
    },
    author="Arnaud Miribel",
    author_email="arnaudmiribel@gmail.com",
    python_requires=">=3.9",
    license="Apache 2",
    install_requires=INSTALL_REQUIRES,
)
