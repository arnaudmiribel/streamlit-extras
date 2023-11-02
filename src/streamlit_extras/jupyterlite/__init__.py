from streamlit.components.v1 import iframe

from .. import extra

@extra
def jupyterlite(height:int,width:int):

    iframe(
        src="https://jupyterlite.github.io/demo/repl/index.html?kernel=python&toolbar=1", 
        height=height,
        width=width
    )

def example():
    jupyterlite(1500,1600)

__title__ = "Jupyterlite"  # title of your extra!
__desc__ = "Add a Jupyterlite sandbox to your Streamlit app in one command" 
__icon__ = "💡"  # give your extra an icon!
__examples__ = [example]  # create some examples to show how cool your extra is!
__author__ = "Rahul Chauhan"
__experimental_playground__ = False  # Optional
