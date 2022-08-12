from nturl2path import url2pathname

from . import main

__func__ = main.table_with_images
__title__ = "Image in tables"
__desc__ = "Transform URLs into images in your dataframes"
__icon__ = "🚩"
__examples__ = [main.example]
__inputs__ = dict(df=main.df)
