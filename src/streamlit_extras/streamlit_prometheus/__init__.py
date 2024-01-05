from typing import Dict, List, NamedTuple, Optional

from prometheus_client import CollectorRegistry
from prometheus_client.registry import Collector
from prometheus_client.utils import floatToGoString
from streamlit.runtime.stats import CacheStatsProvider

from .. import extra


class CustomStat(NamedTuple):
    name: str = ""
    labelstr: str = ""
    value: float = 0
    metadata_str: str = ""

    def to_metric_str(self) -> str:
        if self.metadata_str:
            return self.metadata_str
        return "{}{} {}".format(
            self.name,
            self.labelstr,
            floatToGoString(self.value),
        )


class PrometheusMetricsProvider(CacheStatsProvider):
    def __init__(self, registry: CollectorRegistry):
        self.registry = registry

    def get_stats(self) -> List[CustomStat]:
        output = []
        # This code is taken almost verbatim from
        # https://github.com/prometheus/client_python/blob/34553ad4cf606d96085e4094c283ba46a2a0f764/prometheus_client/openmetrics/exposition.py#L18
        # TODO: Figure out if there's a cleaner way to handle this
        for metric in self.registry.collect():
            try:
                mname = metric.name
                # [JC] Should type come before help? I swapped these to match what Streamlit does but I'm not sure
                output.append(CustomStat(metadata_str=f"# TYPE {mname} {metric.type}"))
                output.append(
                    CustomStat(
                        metadata_str="# HELP {} {}".format(
                            mname,
                            metric.documentation.replace("\\", r"\\")
                            .replace("\n", r"\n")
                            .replace('"', r"\""),
                        )
                    )
                )
                if metric.unit:
                    output.append(
                        CustomStat(metadata_str=f"# UNIT {mname} {metric.unit}")
                    )
                for s in metric.samples:
                    if s.labels:
                        labelstr = "{{{0}}}".format(
                            ",".join(
                                [
                                    '{}="{}"'.format(
                                        k,
                                        v.replace("\\", r"\\")
                                        .replace("\n", r"\n")
                                        .replace('"', r"\""),
                                    )
                                    for k, v in sorted(s.labels.items())
                                ]
                            )
                        )
                    else:
                        labelstr = ""
                    output.append(
                        CustomStat(
                            name=s.name,
                            labelstr=labelstr,
                            value=s.value,
                        )
                    )
            except Exception as exception:
                exception.args = (exception.args or ("",)) + (metric,)
                raise
        return output


class StreamlitCollectorRegistry(CollectorRegistry):
    """Streamlit specific CollectorRegistry that handles the multiple-rerun behavior for registering metric collectors."""

    # TODO: Note the class currently has a bug where metrics created in the cache will stop working if the cache is cleared
    #       Figure out if there's a way to fix / merge?
    def __init__(
        self, auto_describe: bool = False, target_info: Optional[Dict[str, str]] = None
    ):
        super().__init__(auto_describe=auto_describe, target_info=target_info)

    def register(self, collector: Collector) -> None:
        """Register the collector, ensuring it only gets registered once with Streamlit's execution model"""
        # TODO: Figure out a cleaner way, that also handles case where other args have changed
        if collector._get_metric().name in self._names_to_collectors.keys():
            return
        return super().register(collector)


@extra
def streamlit_registry() -> StreamlitCollectorRegistry:
    """
    Expose Prometheus metrics (https://prometheus.io) from your Streamlit app.

    Create and use Prometheus metrics in your app with `registry=streamlit_registry()`.
    The metrics will be exposed at Streamlit's existing `/_stcore/metrics` route.

    See more example metrics in the Prometheus Python docs:
    https://prometheus.github.io/client_python/

    Note: To produce accurate metrics, you are responsible to ensure that unique metric
    objects are shared across app runs and sessions. We recommend initializing metrics
    in a cached function as shown in the example below.

    For an app running locally you can view the output with
    `curl localhost:8501/_stcore/metrics` or equivalent.
    """
    from streamlit.runtime import Runtime

    stats = Runtime.instance().stats_mgr

    # Did we already register it in another session?
    for prv in stats._cache_stats_providers:
        if isinstance(prv, PrometheusMetricsProvider):
            return prv.registry

    # This is the first session on the server, create and register
    registry = StreamlitCollectorRegistry(auto_describe=True)
    prv = PrometheusMetricsProvider(registry=registry)
    stats.register_provider(prv)
    print("Initialized custom metrics provider")
    return registry


def example():
    import streamlit as st
    from prometheus_client import Counter

    @st.cache_resource
    def get_metric():
        registry = streamlit_registry()
        return Counter(
            name="my_counter",
            documentation="A cool counter",
            labelnames=("app_name",),
            registry=registry,  # important!!
        )

    SLIDER_COUNT = get_metric()

    app_name = st.text_input("App name", "prometheus_app")
    latest = st.slider("Latest value", 0, 20, 3)
    if st.button("Submit"):
        SLIDER_COUNT.labels(app_name).inc(latest)

    """
    ### Example output at `{host:port}/_stcore/metrics`
    ```
    # TYPE my_counter counter
    # HELP my_counter A cool counter
    my_counter_total{app_name="prometheus_app"} 14.0
    my_counter_created{app_name="prometheus_app"} 1.7042185907557938e+09
    ```
    """


__title__ = "Streamlit Prometheus"
__desc__ = "Expose Prometheus metrics (https://prometheus.io) from your Streamlit app."
__icon__ = "📊"
__examples__ = [example]
__author__ = "Joshua Carroll"
__experimental_playground__ = False
__stlite__ = False
