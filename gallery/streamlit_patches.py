import sys
from pathlib import Path
from time import sleep
from typing import Any, Callable, Dict, List, Optional, Union

import requests
from streamlit import *
from streamlit import (
    error,
    experimental_singleton,
    runtime,
    source_util,
)
from streamlit.commands.page_config import get_random_emoji
from streamlit.runtime.scriptrunner import get_script_run_ctx as _get_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import (
    LOGGER,
    SCRIPT_RUN_WITHOUT_ERRORS_KEY,
    ForwardMsg,
    RerunData,
    RerunException,
    ScriptRunner,
    ScriptRunnerEvent,
    StopException,
    _clean_problem_modules,
    _log_if_error,
    _new_module,
    config,
    handle_uncaught_app_exception,
    magic,
    modified_sys_path,
)
from streamlit.source_util import _on_pages_changed, get_pages
from streamlit.util import calc_md5


@experimental_singleton
def get_icons() -> Dict[str, str]:
    url = "https://raw.githubusercontent.com/omnidan/node-emoji/master/lib/emoji.json"
    return requests.get(url).json()


def translate_icon(icon: str) -> str:
    """
    If you pass a name of an icon, like :dog:, translate it into the
    corresponding unicode character
    """
    icons = get_icons()
    if icon == "random":
        icon = get_random_emoji()
    elif icon[0] == icon[-1] == ":":
        icon = icon[1:-1]
        if icon in icons:
            return icons[icon]
    return icon


def page(
    path: Union[str, Callable],
    name: Optional[str] = None,
    icon: Optional[str] = None,
):
    """
    Add a new page to the sidebar
    path: The path to the page's script or a function that returns the page's script
    name (optional): The name of the page (defaults to the page's script's or function
    name, with underscores replaced with spaces)
    icon (optional): The icon to be used for the page. Can either be the actual icon
        (e.g. 🔥) or with colons around the name (e.g. :fire:), or "random" for a random
        emoji
    """

    # TODO -- FIX THIS
    main_script_path = "gallery/streamlit_app.py"

    main_page_hash = calc_md5(main_script_path)

    main_script_path_absolute = Path(main_script_path).absolute()

    main_page_hash_absolute = calc_md5(str(main_script_path_absolute))

    page_config = get_pages(main_script_path)

    if main_page_hash in page_config:
        page_config.pop(main_page_hash)

    if main_page_hash_absolute in page_config:
        page_config.pop(main_page_hash_absolute)

    if callable(path):
        page_script_hash = calc_md5(path.__name__)
    else:
        page_script_hash = calc_md5(path)

    # If this page has already been added, don't try to add it again.
    if page_script_hash in page_config:
        return

    ctx = _get_script_run_ctx()
    if ctx is None:
        return

    if name is None:
        if callable(path):
            name = path.__name__.replace("_", " ")
        else:
            name = str(path).replace("_", " ").replace(".py", "")

    config: Dict[str, Any] = {
        "page_name": name,
    }
    if icon is not None:
        config["icon"] = translate_icon(icon)
    else:
        config["icon"] = ""

    config["real_script_path"] = path

    config["script_path"] = main_script_path

    config["page_script_hash"] = page_script_hash

    page_config[page_script_hash] = config

    _on_pages_changed.send()

    sleep(0.1)


def _run_script(self, rerun_data: RerunData) -> None:
    """Run our script.

    Parameters
    ----------
    rerun_data: RerunData
        The RerunData to use.

    """
    assert self._is_in_script_thread()

    LOGGER.debug("Running script %s", rerun_data)

    # Reset DeltaGenerators, widgets, media files.
    runtime.get_instance().media_file_mgr.clear_session_refs()

    pages = source_util.get_pages(self._main_script_path)
    # Safe because pages will at least contain the app's main page.
    main_page_info = list(pages.values())[0]
    current_page_info = None

    if rerun_data.page_script_hash:
        current_page_info = pages.get(rerun_data.page_script_hash, None)
    elif not rerun_data.page_script_hash and rerun_data.page_name:
        # If a user navigates directly to a non-main page of an app, we get
        # the first script run request before the list of pages has been
        # sent to the frontend. In this case, we choose the first script
        # with a name matching the requested page name.
        current_page_info = next(
            filter(
                # There seems to be this weird bug with mypy where it
                # thinks that p can be None (which is impossible given the
                # types of pages), so we add `p and` at the beginning of
                # the predicate to circumvent this.
                lambda p: p and (p["page_name"] == rerun_data.page_name),
                pages.values(),
            ),
            None,
        )
    else:
        # If no information about what page to run is given, default to
        # running the main page.
        current_page_info = main_page_info

    page_script_hash = (
        current_page_info["page_script_hash"]
        if current_page_info is not None
        else main_page_info["page_script_hash"]
    )

    ctx = self._get_script_run_ctx()
    ctx.reset(
        query_string=rerun_data.query_string,
        page_script_hash=page_script_hash,
    )

    self.on_event.send(
        self,
        event=ScriptRunnerEvent.SCRIPT_STARTED,
        page_script_hash=page_script_hash,
    )

    # Compile the script. Any errors thrown here will be surfaced
    # to the user via a modal dialog in the frontend, and won't result
    # in their previous script elements disappearing.
    try:
        if current_page_info:
            script_path = current_page_info["script_path"]
            extra_script_path = current_page_info.get("real_script_path")
        else:
            script_path = self._main_script_path
            extra_script_path = None

            # At this point, we know that either
            #   * the script corresponding to the hash requested no longer
            #     exists, or
            #   * we were not able to find a script with the requested page
            #     name.
            # In both of these cases, we want to send a page_not_found
            # message to the frontend.
            msg = ForwardMsg()
            msg.page_not_found.page_name = rerun_data.page_name
            ctx.enqueue(msg)

        code: List[Any] = [_get_code_from_path(script_path)]

        if extra_script_path is not None:
            if type(extra_script_path) == str:
                code.append(_get_code_from_path(extra_script_path))
            elif callable(extra_script_path):
                code.append(extra_script_path)
            else:
                error(extra_script_path)
                raise NotImplementedError("Must pass a file path or function")

    except BaseException as e:
        # We got a compile error. Send an error event and bail immediately.
        LOGGER.debug("Fatal script error: %s", e)
        self._session_state[SCRIPT_RUN_WITHOUT_ERRORS_KEY] = False
        self.on_event.send(
            self,
            event=ScriptRunnerEvent.SCRIPT_STOPPED_WITH_COMPILE_ERROR,
            exception=e,
        )
        return

    # If we get here, we've successfully compiled our script. The next step
    # is to run it. Errors thrown during execution will be shown to the
    # user as ExceptionElements.

    if config.get_option("runner.installTracer"):
        self._install_tracer()

    # This will be set to a RerunData instance if our execution
    # is interrupted by a RerunException.
    rerun_exception_data: Optional[RerunData] = None

    try:
        # Create fake module. This gives us a name global namespace to
        # execute the code in.
        # TODO(vdonato): Double-check that we're okay with naming the
        # module for every page `__main__`. I'm pretty sure this is
        # necessary given that people will likely often write
        #     ```
        #     if __name__ == "__main__":
        #         ...
        #     ```
        # in their scripts.
        module = _new_module("__main__")

        # Install the fake module as the __main__ module. This allows
        # the pickle module to work inside the user's code, since it now
        # can know the module where the pickled objects stem from.
        # IMPORTANT: This means we can't use "if __name__ == '__main__'" in
        # our code, as it will point to the wrong module!!!
        sys.modules["__main__"] = module

        # Add special variables to the module's globals dict.
        # Note: The following is a requirement for the CodeHasher to
        # work correctly. The CodeHasher is scoped to
        # files contained in the directory of __main__.__file__, which we
        # assume is the main script directory.
        module.__dict__["__file__"] = script_path

        with modified_sys_path(self._main_script_path), self._set_execing_flag():
            # Run callbacks for widgets whose values have changed.
            if rerun_data.widget_states is not None:
                self._session_state.on_script_will_rerun(rerun_data.widget_states)

            ctx.on_script_start()
            # write(code)
            for c in code:
                if callable(c):
                    c()
                else:
                    exec(c, module.__dict__)
                # write(module.__dict__)
            self._session_state[SCRIPT_RUN_WITHOUT_ERRORS_KEY] = True
    except RerunException as e:
        rerun_exception_data = e.rerun_data

    except StopException:
        pass

    except BaseException as e:
        self._session_state[SCRIPT_RUN_WITHOUT_ERRORS_KEY] = False
        handle_uncaught_app_exception(e)

    finally:
        if rerun_exception_data:
            finished_event = ScriptRunnerEvent.SCRIPT_STOPPED_FOR_RERUN
        else:
            finished_event = ScriptRunnerEvent.SCRIPT_STOPPED_WITH_SUCCESS
        self._on_script_finished(ctx, finished_event)

    # Use _log_if_error() to make sure we never ever ever stop running the
    # script without meaning to.
    _log_if_error(_clean_problem_modules)

    if rerun_exception_data is not None:
        self._run_script(rerun_exception_data)


def _get_code_from_path(script_path: str) -> Any:
    with source_util.open_python_file(script_path) as f:
        filebody = f.read()

    if config.get_option("runner.magicEnabled"):
        filebody = magic.add_magic(filebody, script_path)

    code = compile(
        filebody,
        # Pass in the file path so it can show up in exceptions.
        script_path,
        # We're compiling entire blocks of Python, so we need "exec"
        # mode (as opposed to "eval" or "single").
        mode="exec",
        # Don't inherit any flags or "future" statements.
        flags=0,
        dont_inherit=1,
        # Use the default optimization options.
        optimize=-1,
    )

    return code


ScriptRunner._run_script = _run_script  # type: ignore
