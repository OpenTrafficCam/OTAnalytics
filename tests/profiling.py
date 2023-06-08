"""
Profiling provides a decorator to profile a python function by annotating it.
It measures execution time of annotated functions
and provides several configuration options such as:
- number of measured executions
- number of executions before measurement for cache warmup
- ...
"""


import functools
from cProfile import Profile
from datetime import datetime
from io import StringIO
from os import walk
from os.path import join, splitext
from pathlib import Path
from pstats import SortKey, Stats
from time import perf_counter
from typing import Any, Callable, Iterator

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import plotly.graph_objects as go
from plotly.offline import plot

SEP = ";"


def profile(
    repeat: int = 5,
    warmup: int = 0,
    output: str = "profiles/{M}/{N}/{D}/profile_{N}_{D}_{T}.csv",
    write_console: bool = False,
    result: int | str = -1,
    plot: str | None = "sankey",
) -> Callable[[Callable], Callable]:
    """profile decorates an annotated function to profile their execution time.

    Pythons internal cProfile is used to measure execution times, function calls, etc.
    The measurement of the annotated function can be repeated multiple times.
    Moreover, warmup executions before measurement can be used for cache warmup.

    All measurements are exported in csv format at the specified location
    using the provided file name template:
    - The placeholder '{N}' is replaced by the annotated function's name
    - The placeholder '{M}' is replaced by the module of the annotated function's name
    - The placeholder '{D}' is replaced by the current date (DD-MM-YYY)
    - The placeholder '{T}' is replaced by the current time (HH-MM-SS)
    E.g. the template 'profiles/{M}/{N}/{D}/profile_{N}_{D}_{T}.csv' may result in
    'profiles/profile_my_func_12-08-1979_12-42-07.csv'.

    Finally the kind of plots to produce can be specified:
    "pie", "graph", "sankey", a combination of the three with a "|" seperator,
    "all" or None are available.

    Args:
        repeat (int, optional): the number of measured executions.
            Defaults to 5.
        warmup (int, optional): the number of unmeasured warmup executions.
            Defaults to 0.
        output (str, optional): the output file template.
            Defaults to "profiles/{M}/{N}/{T}/profile_{N}_{D}_{T}.csv".
        write_console (bool, optional): whether stats should be printed on console.
            Defaults to False.
        result (int | str): indicates what the wrapped function should return.
            Either the index (int) of which execution's result should be returned
            or "path" to return the path of the profiling result file.
            Defaults to -1.
        plot (str | None, optional): the kind of plots to produce.
            "pie", "graph", "sankey", a combination of the three with a
            "|" seperator, "all" or None are supported.
            Defaults to "all".

    Returns:
        Callable[[Callable], Callable]: the profiling decorator to annotate a function
    """
    writer = ProfileWriter(output, repeat, write_console)
    return Profiler(writer, repeat, warmup, result, plot).as_decorator


class ProfileWriter:
    """ProfileWriter is a class for converting cProfile stats to csv format.

    Args:
        output (str): the output file template where the csv result is saved
        runs (int): the number of executions that were measured
        write_console (bool): whether stats should be printed to the console
    """

    def __init__(self, output: str, runs: int, write_console: bool) -> None:
        """Creates a new ProfileWriter.

        Args:
            output (str): the output file template where the csv result is saved
            runs (int): the number of executions that were measured
            write_console (bool): whether stats should be printed to the console
        """
        self.output = output
        self.runs = runs
        self.write_console = write_console

    def write(self, profile: Profile, func_name: str, module_name: str) -> str:
        """Converts the measured stats to csv format
        and writes them to the specified file location.

        Args:
            profile (Profile): the measured profile to be converted to csv
            func_name (str): the name of the measured function
            module_name (str): the name of the measured function's module

        Returns:
            str: path of the saved file
        """
        calls = self.stats_to_rows(
            profile,
            stat_printer=lambda stats: stats.print_callers(),
            line_parser=self.parse_caller,
        )
        caller_map = {callee: caller for caller, callee in calls}

        rows = self.stats_to_rows(
            profile,
            stat_printer=lambda stats: stats.print_stats(),
            line_parser=lambda line: self.parse_measures(line, caller_map),
        )
        csv = self.rows_to_csv([self.header()] + rows)

        path = self.create_file_name(func_name, module_name)
        self.write_to_file(csv, path)

        dump_path = self.to_dump_path(path)
        profile.dump_stats(dump_path)
        return path

    def to_dump_path(self, path: str) -> str:
        """Creates a path for the stats dump derived from the given path.
            Replaces the file extension by ".dump".

        Args:
            path (str): the path to be converted to a dump path

        Returns:
            str: the derived dump path
        """
        return splitext(path)[0] + ".dump"

    def stats_to_rows(
        self,
        profile: Profile,
        stat_printer: Callable[[Stats], Stats],
        line_parser: Callable[[str], list[Any] | None],
    ) -> list[list[Any]]:
        """Extracts stats from the given profile and parses them to individual rows.

        Different stats can be extracted by providing a print_<XY>() function
        of pstats.Stats:
        e.g. 'lambda s: s.print_stats()'  or 'lambda s: s.print_callers()'.

        The extracted stats table is parsed line by line using the provided line_parser.

        Args:
            profile (Profile): the measured profile to be evaluated
            stat_printer (Callable[[Stats], Stats]): the stats extraction function
            line_parser (Callable[[str], list[Any]  |  None]): a parser for lines of the
                extracted stats; converts line string to list of values or discards it

        Returns:
            list[list[Any]]: a matrix of rows, each containing measured values
                extracted from the stats
        """
        stats = StringIO()
        stat_printer(
            Stats(profile, stream=stats).strip_dirs().sort_stats(SortKey.CUMULATIVE)
        )

        if self.write_console:
            print(stats.getvalue())

        # remove text preceding first column header
        table = stats.getvalue().split("ncalls")[-1]

        # split lines and drop stats header
        lines = table.splitlines()[1:]
        lines = [line for line in lines if len(line) > 0]

        rows = [line_parser(line) for line in lines]
        return [r for r in rows if r is not None and len(r) > 0]

    def header(self) -> list[str]:
        """Creates the header for csv format.

        Returns:
            list[str]: header with column names of the csv format
        """
        return ["ncalls", "tries", "tottime", "cumtime", "function", "called_by"]

    def parse_measures(self, line: str, caller_map: dict[str, str]) -> list[Any]:
        """Parses measurement stats by extracting number of calls,
        total time, cumulated time, function name.
        Also adds number of executions and caller name for each row.

        Args:
            line (str): the line to be parsed
            caller_map (dict[str, str]): a mapping from function name to its caller

        Raises:
            ValueError: if the given line cannot be parsed

        Returns:
            list[Any]: a list of measured values:
                "ncalls", "tries", "tottime", "cumtime", "function", "called_by"
        """
        try:
            ncalls, tottime, _, cumtime, _, function = line.split(None, 5)
        except ValueError:
            raise ValueError(
                "Could not identify fields 'ncalls', 'tottime', (percall), 'cumtime',"
                + f"(percall), 'function' in line '{line}' -> {line.split(None, 5)}"
            )

        callee = function.strip()
        return [ncalls, self.runs, tottime, cumtime, callee, caller_map.get(callee, "")]

    def parse_caller(self, line: str) -> list[str] | None:
        """Parses caller stats and extracts the calling function
        for each called function.

        Args:
            line (str): the line to be parsed

        Returns:
            list[str] | None: caller, callee or None
                if the given line could not be parsed
        """
        if "<-" in line:
            callee, rest = line.split("<-")

            if len(rest.strip()) > 0:
                caller = rest.split(None, 3)[-1]
                return [caller.strip(), callee.strip()]

        return None

    def rows_to_csv(self, rows: list[list[Any]]) -> str:
        """Converts matrix of rows to csv format.

        Args:
            rows (list[list[Any]]): a matrix of rows

        Returns:
            str: lines of comma separated rows containing the given values
        """
        return "\n".join([SEP.join(map(str, row)) for row in rows])

    def write_to_file(self, csv: str, path: str) -> None:
        """Writes the given csv string into the file at the given path.

        Args:
            csv (str): the csv string to be saved to file
            path (str): the path of the result file
        """

        file = Path(path)
        file.parent.mkdir(exist_ok=True, parents=True)
        file.write_text(csv)

    def create_file_name(self, func_name: str, module_name: str) -> str:
        """Renders the output file template using the
        given function name as well as current time and date.

        Args:
            func_name (str): name of the profiled function
            module_name (str): name of the profiled function's module

        Returns:
            str: the rendered output file template
        """
        now = datetime.now()

        path = self.output
        path = path.replace("{T}", now.strftime("%H-%M-%S"))
        path = path.replace("{D}", now.strftime("%d-%m-%Y"))
        path = path.replace("{M}", module_name)
        path = path.replace("{N}", func_name)

        return path


class Profiler:
    """Profiler is a class to execute profiling on a given function.

    Args:
        writer (ProfileWriter): the ProfileWriter to be used
            for writing measurements to files.
        repeat (int): the number of measured executions.
        warmup (int): the number of unmeasured warmup executions.
        result (int | str): indicates what the wrapped function should return.
            Either the index (int) of which execution's result should be returned
            or "path" to return the path of the profiling result file.
            Defaults to "path".
        plot (str | None, optional): the kind of plots to produce.
            "pie", "graph", "sankey", a combination of the three with a
            "|" seperator, "all" or None are supported.
            Defaults to "all".
    """

    def __init__(
        self,
        writer: ProfileWriter,
        repeat: int,
        warmup: int,
        result: int | str = "path",
        plot: str | None = "all",
    ) -> None:
        """Creates a new Profiler.

        Args:
            writer (ProfileWriter): the ProfileWriter to be used
                for writing measurements to files.
            repeat (int): the number of measured executions.
            warmup (int): the number of unmeasured warmup executions.
            result (int | str): indicates what the wrapped function should return.
                Either the index (int) of which execution's result should be returned
                or "path" to return the path of the profiling result file.
                Defaults to "path".
            plot (str | None, optional): the kind of plots to produce.
                "pie", "graph", "sankey", a combination of the three with a
                "|" seperator, "all" or None are supported.
                Defaults to "all".
        """
        self.writer = writer
        self.repeat = repeat
        self.warmup = warmup
        self.result = result
        self.plot = plot

    def run(self, execution: Callable) -> tuple[list, Profile]:
        """Runs the warmup and profiling executions of the given function.

        Args:
            execution (Callable): the function to be profiled

        Returns:
            tuple[list, Profile]: the list of execution results
                and the generated Profile
        """
        results = []

        for _ in range(self.warmup):
            results.append(execution())

        profile = Profile()
        for i in range(self.repeat):
            start = perf_counter()
            profile.enable()
            res = execution()
            profile.disable()
            end = perf_counter()

            print(f"Run {i} took {end-start}")

            results.append(res)

        return results, profile

    def as_decorator(self, func: Callable) -> Callable:
        """Converts the Profiler to a decorator by creating
        a wrapper for the given function which executes the profiling.

        Args:
            func (Callable): the function to be profiled.

        Returns:
            Callable: a wrapper for the given function
        """

        @functools.wraps(func)
        def profiling_wrapper(*args: Any, **kwargs: Any) -> Any:
            results, profile = self.run(lambda: func(*args, **kwargs))
            path = self.writer.write(profile, func.__name__, str(func.__qualname__))

            ProfilePlotter().create_plot(path, func.__name__, kind=self.plot)

            match self.result:
                case "path":
                    return path
                case int(self.result):
                    return results[self.result]

        return profiling_wrapper


class ProfilePlotter:
    """The ProfilePlotter class provides the means to plot
    the time measurements and call structure of a function's profile.
    It currently supports three representations: graph, pie and sankey.
    """

    def __init__(self) -> None:
        self.plotters = {
            "pie": self.as_pie,
            "graph": self.as_graph,
            "sankey": self.as_sankey,
        }

    def update_plots(
        self, path: str, kind: str | None = "pie", recursive: bool = True
    ) -> None:
        for f in self.collect_csv(path, recursive):
            name = f.split("\\")[-1]
            self.create_plot(file=f, name=name, kind=kind)

    def collect_csv(self, path: str, recursive: bool = True) -> Iterator[str]:
        for dirpath, _, filenames in walk(path):
            yield from [join(dirpath, f) for f in filenames if f.endswith(".csv")]

            if not recursive:
                break

    def create_plot(
        self,
        file: str,
        name: str,
        kind: str | None = "pie",
        depth: int = 9,
        min_fract: float = 0.05,
    ) -> None:
        """Creates plots of the given kind for the profile in the given file.

        Args:
            file (str): path to the file containing the profile results.
            name (str): name of the profiled function
            kind (str | None, optional): defines the kind(s) of plots to create.
                Supported kinds are "pie", "graph" and "sankey"
                or a concatenation of these with "|" as separator: e.g. "pie|sankey".
                If None or "" are given, no plots re produced.
                Defaults to "pie".
            depth (int): defines depth of function call tree to be plotted.
                Defaults to 15.
            min_fract (int): defines minimum fraction of maximum cumtime
                for measurements o be plotted. Defaults to 15.
        """
        if kind is None or kind == "":
            return None

        data = self.prepare_data(file, depth, min_fract)

        plot_funcs = (
            self.plotters.values()
            if kind == "all"
            else [self.plotters.get(k, self.as_pie) for k in set(kind.split("|"))]
        )

        for plotter in plot_funcs:
            fig, extension = plotter(data, name)
            path = file.replace(".csv", extension)
            self.save(fig, path)

    def save(self, fig: go.Figure | None, output: str) -> None:
        """Saves the created figure at the given output path.
            Uses the plotly save mechanism if a plotly Figure is given.
            Uses the global matplotlib save mechanism, if None is given.

        Args:
            fig (go.Figure | None): the plotly figure to save
                or None if the global matplotlib figure should be saved.
            output (str): path to the result file for storing the figures
        """
        if fig is None:
            plt.savefig(output, format="PNG")
        else:
            config = {
                "displaylogo": False,
                "scrollZoom": True,
            }
            plot(fig, filename=output, auto_open=False, config=config)

    def prepare_data(
        self, file: str, call_depth: int = 15, min_fract: float = 0.01
    ) -> pd.DataFrame:
        """Reads the data from the given profile csv file and creates a dataframe.

        Args:
            file (str): path to the profile csv file to be read
            call_depth (int): depth in function call hierarchy
                up to which profile measurements should be returned.
                If less than 0, all measurements are returned.
            min_fract (float): filter measurements with
                less than the given fraction of the maximum "cumtime".

        Returns:
            pd.DataFrame: DataFrame containing the  measurements of the profile
        """
        df = pd.read_csv(file, sep=SEP)
        df["called_by"] = df["called_by"].fillna("")

        if call_depth > 0:
            visited = [""]
            for _ in range(call_depth):
                called = df[df["called_by"].isin(visited)]["function"]
                visited += [c for c in called if c not in visited]

        df = df[df["called_by"].isin(visited) | df["function"].isin(visited)]

        df = df[df["cumtime"] >= df["cumtime"].max() * 0.01]
        return df

    def as_graph(
        self, data: pd.DataFrame, name: str, attr: str = "cumtime"
    ) -> tuple[None, str]:
        """Creates a graph plot from the profile data.

        Args:
            data (pd.DataFrame): the profile data to be plotted.
                Requires a "funtion", "called_by" column
                as well as the specified attr(ibute) column.
            name (str): name of the profiled function
            attr (str, optional): The attribute column to be evaluated.
                Defaults to "cumtime".

        Returns:
            tuple[None, str]: No figure is returned as matplotlib uses a global store.
                The graph file extension is returned.
        """
        nodes = zip(data["function"], data[attr])
        edges = zip(data["function"], data["called_by"])

        G = nx.MultiDiGraph(seed=42)
        [G.add_node(v, time=t) for v, t in nodes]
        [G.add_edge(u, v) for v, u in edges if u != ""]
        size = [(n[1]["time"] * 10) ** 2 for n in G.nodes().data()]
        labels = {n[0]: f"{n[0]}:\n{n[1]['time']}" for n in G.nodes().data()}

        nx.draw(
            G,
            labels=labels,
            node_size=size,
            with_labels=True,
            cmap=plt.get_cmap("jet"),
            node_color=size,
        )

        return None, "_graph.png"

    def as_pie(
        self, data: pd.DataFrame, name: str, attr: str = "cumtime"
    ) -> tuple[go.Sunburst, str]:
        """Creates a (sunburst)-pie plot from the profile data.

        Args:
            data (pd.DataFrame): the profile data to be plotted.
                Requires a "funtion", "called_by" column
                as well as the specified attr(ibute) column.
            name (str): name of the profiled function
            attr (str, optional): The attribute column to be evaluated.
                Defaults to "cumtime".

        Returns:
            tuple[go.Sunburst, str]: Returns the sunburst representation of the data.
                Also returns the file extension for pie plots.
        """
        ids = data["function"]
        labels = data["function"]
        parents = data["called_by"]
        values = data[attr]

        trace = go.Sunburst(
            ids=ids, labels=labels, parents=parents, values=values, branchvalues="total"
        )
        layout = go.Layout(template="plotly_white", title=name)

        fig = go.Figure(data=[trace], layout=layout)

        return fig, "_pie.html"

    def as_sankey(
        self, data: pd.DataFrame, name: str, attr: str = "cumtime"
    ) -> tuple[go.Sankey, str]:
        """Creates a sankey plot from the profile data.

        Args:
            data (pd.DataFrame): the profile data to be plotted.
                Requires a "funtion", "called_by" column
                as well as the specified attr(ibute) column.
            name (str): name of the profiled function
            attr (str, optional): The attribute column to be evaluated.
                Defaults to "cumtime".

        Returns:
            tuple[go.Sankey, str]: Returns the sunburst representation of the data.
            Also returns the file extension for pie plots.
        """
        labels = list(set(data["function"].unique()).union(data["called_by"].unique()))
        if "" in labels:
            labels.remove("")
        id_map = {v: i for i, v in enumerate(labels)}

        links = list(zip(data["function"], data["called_by"], data[attr]))
        links = [
            (id_map[target], id_map[source], value)
            for target, source, value in links
            if source != ""
        ]

        trace = go.Sankey(
            arrangement="freeform",
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue",
            ),
            link=dict(
                source=[s for _, s, _ in links],
                target=[t for t, _, _ in links],
                value=[v for _, _, v in links],
            ),
        )
        layout = go.Layout(template="plotly_white", title=name)

        fig = go.Figure(data=[trace], layout=layout)

        return fig, "_sankey.html"


#  ##################################################
# version1
@profile(repeat=1000, warmup=10, write_console=True)
def fib_iter(num: int) -> int:
    if num == 0:
        return 0

    second_to_last = 0
    last = 1

    for _ in range(1, num):
        second_to_last, last = last, second_to_last + last

    return last


@profile(repeat=1000, warmup=10, write_console=True)
def fib_rec_wrap(num: int) -> int:
    return fib_rec(num)


def fib_rec(num: int) -> int:
    return num if num <= 1 else fib_rec(num - 1) + fib_rec(num - 2)


if __name__ == "__main__":
    ProfilePlotter().update_plots("profiles", kind="sankey", recursive=True)
