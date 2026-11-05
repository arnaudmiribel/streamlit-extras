from collections import UserDict
from contextlib import nullcontext

import pandas as pd
import pytest

from streamlit_extras import chart_container as chart_module


class FakeSessionState(UserDict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        if key == "data":
            object.__setattr__(self, key, value)
        else:
            self[key] = value


@pytest.mark.parametrize("filename", [None, "data", "sales_report"])
def test_chart_container_export_filename(monkeypatch, filename):
    downloaded_filenames = []

    monkeypatch.setattr(chart_module.st, "session_state", FakeSessionState())
    monkeypatch.setattr(
        chart_module.st,
        "tabs",
        lambda _labels: (nullcontext(), nullcontext(), nullcontext()),
    )
    monkeypatch.setattr(chart_module.st, "dataframe", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(chart_module.st, "caption", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        chart_module.st,
        "download_button",
        lambda *_args, **kwargs: downloaded_filenames.append(kwargs["file_name"]),
    )

    monkeypatch.setattr(
        chart_module,
        "_SUPPORTED_EXPORTS",
        {
            "CSV": {
                "function": lambda _data: b"csv",
                "extension": ".csv",
                "mime": "text/csv",
            },
            "Parquet": {
                "function": lambda _data: b"parquet",
                "extension": ".parquet",
                "mime": "application/octet-stream",
            },
        },
    )

    kwargs = {} if filename is None else {"filename": filename}

    with chart_module.chart_container(
        pd.DataFrame({"value": [1, 2]}),
        **kwargs,
    ):
        pass

    expected_filename = "data" if filename is None else filename

    assert downloaded_filenames == [
        f"{expected_filename}.csv",
        f"{expected_filename}.parquet",
    ]
