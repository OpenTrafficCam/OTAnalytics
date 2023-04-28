"""
Profiling provides a decorator to profile a python function by annotating it.
It measures execution time of annotated functions
and provides several configuration options such as:
- number of measured executions
- number of executions before measurement for cache warmup
- ...
"""


import functools
import random
from cProfile import Profile
from datetime import datetime
from io import StringIO
from pathlib import Path
from pstats import Stats
from typing import Any, Callable

import pandas as pd
import plotly.graph_objects as go

random.seed(20)


def profile(
    repeat: int = 5,
    warmup: int = 0,
    output: str = "profiles/profile_{N}_{D}_{T}.csv",
    write_console: bool = False,
) -> Callable[[Callable], Callable]:
    """profile decorates an annotated function to profile their execution time.

    Pythons internal cProfile is used to measure execution times, function calls, etc.
    The measurement of the annotated function can be repeated multiple times.
    Moreover, warmup executions before measurement can be used for cache warmup.


    All measurements are exported in csv format at the specified location
    using the provided file name template:
    - The placeholder '{N}' is replaced by the annotated functions name
    - The placeholder '{D}' is replaced by the current date (DD-MM-YYY)
    - The placeholder '{D}' is replaced by the current time (HH-MM-SS)
    E.g. the template 'profiles/profile_{N}_{D}_{T}.csv' may result in
    'profiles/profile_my_func_12-08-1979_12-42-07.csv'.

    Args:
        repeat (int, optional): the number of measured executions.
            Defaults to 5.
        warmup (int, optional): the number of unmeasured warmup executions.
            Defaults to 0.
        output (str, optional): the output file template.
            Defaults to "profiles/profile_{N}_{D}_{T}.csv".
        write_console (bool, optional): whether stats should be printed on console.
            Defaults to False.

    Returns:
        Callable[[Callable], Callable]: the profiling decorator to annotate a function
    """
    writer = ProfileWriter(output, repeat, write_console)
    return Profiler(writer, repeat, warmup).as_decorator


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

    def write(self, profile: Profile, func_name: str) -> None:
        """Converts the measured stats to csv format
        and writes them to the specified file location.

        Args:
            profile (Profile): the measured profile to be converted to csv
            func_name (str): the name of the measured function
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
        self.write_to_file(csv, func_name)

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
        stat_printer(Stats(profile, stream=stats).strip_dirs())

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
            str: _description_
        """
        return "\n".join([",".join(map(str, row)) for row in rows])

    def write_to_file(self, csv: str, func_name: str) -> None:
        path = self.create_file_name(func_name)

        file = Path(path)
        file.parent.mkdir(exist_ok=True, parents=True)
        file.write_text(csv)

    def create_file_name(self, func_name: str) -> str:
        now = datetime.now()

        path = self.output
        path = path.replace("{T}", now.strftime("%H-%M-%S"))
        path = path.replace("{D}", now.strftime("%d-%m-%Y"))
        path = path.replace("{N}", func_name)

        return path


class Profiler:
    def __init__(
        self, writer: ProfileWriter, repeat: int, warmup: int, return_index: int = -1
    ) -> None:
        self.writer = writer
        self.repeat = repeat
        self.warmup = warmup
        self.return_index = return_index

    def run(self, execution: Callable) -> tuple[list, Profile]:
        results = []

        for _ in range(self.warmup):
            results.append(execution())

        profile = Profile()
        for _ in range(self.repeat):
            profile.enable()
            res = execution()
            profile.disable()
            results.append(res)

        return results, profile

    def as_decorator(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def profiling_wrapper(*args: Any, **kwargs: Any) -> Any:
            results, profile = self.run(lambda: func(*args, **kwargs))
            self.writer.write(profile, func.__name__)

            return results[self.return_index]

        return profiling_wrapper


class ProfilePlotter:
    def as_pie(self, file: str) -> None:
        data = pd.read_csv(file, sep=";")
        print(data)

        funcs = set(data["caller"].unique())
        funcs.union(set(data["callee"]))
        func_ids = {f: i for i, f in enumerate(funcs)}

        ids = data["callee"].map(func_ids)
        labels = data["callee"]
        parents = data["caller"].map(func_ids)
        values = data["cumtime"]

        traces = [go.Sunburst(ids=ids, labels=labels, parents=parents, values=values)]
        layout = go.Layout(template="plotly_white", title="tests")

        fig = go.Figure(data=traces, layout=layout)
        fig.show()


#  ##################################################
def random_list(num: int) -> list[int]:
    return [random.randint(0, 100) for _ in range(num)]


# version1
@profile(repeat=10, warmup=1, write_console=True)
def count_and_sort(elements: list[int]) -> dict:
    counted = count_elements(elements)
    sorted = sort_elements(counted)
    return sorted


def count_elements(elements: list[int]) -> dict:
    counts = {}
    for e in elements:
        if e not in counts:
            counts[e] = 0
        counts[e] += 1
    return counts


def sort_elements(counts: dict) -> dict:
    return {k: v for k, v in sorted(counts.items(), key=lambda x: x[1])}


if __name__ == "__main__":
    p = random_list(100_000)
    count_and_sort(p)
