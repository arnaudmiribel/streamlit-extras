import base64

from streamlit_avatar import avatar

from .. import extra

avatar = extra(avatar)


def example():
    avatar(
        [
            {
                "url": "https://picsum.photos/id/237/300/300",
                "size": 40,
                "title": "Sam",
                "caption": "hello",
                "key": "avatar1",
            }
        ]
    )


def example_1():
    image_path = "assets/image.png"
    with open(image_path, "rb") as image_file:
        image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    image_url = f"data:image/png;base64,{image_base64}"

    avatar(
        [
            {
                "url": image_url,
                "size": 50,
                "title": "Sam",
                "caption": "hello",
                "key": "avatar1",
            }
        ],
        [
            {
                "url": "https://picsum.photos/id/237/300/300",
                "size": 40,
                "title": "Sam",
                "caption": "hello",
                "key": "avatar1",
            }
        ],
    )


__title__ = "Avatar"  # title of your extra!
__desc__ = "Streamlit Component, for a UI avatar"  # description of your extra!
__icon__ = "👥"  # give your extra an icon!
__examples__ = [
    example,
    example_1,
]  # create some examples to show how cool your extra is!
__author__ = "Saijyoti Tripathy"
__pypi_name__ = "streamlit-avatar"
__package_name__ = "streamlit_avatar"
__playground__ = True
