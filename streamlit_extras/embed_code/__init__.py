from streamlit_embedcode import github_gist


def example_github():
    github_gist(
        "https://gist.github.com/randyzwitch/be8c5e9fb5b8e7b046afebcac12e5087/",
        width=700,
        height=400,
    )


__func__ = github_gist
__title__ = "Embed code"
__desc__ = "Embed code from various platforms (Gists, snippets...)"
__icon__ = "📋"
__examples__ = [example_github]
__author__ = "randyzwitch"
__github_repo__ = "randyzwitch/streamlit-embedcode"
__pypi_name__ = "streamlit-embedcode"
__package_name__ = "streamlit_embedcode"
__experimental_playground__ = False
