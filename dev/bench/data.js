window.BENCHMARK_DATA = {
  "lastUpdate": 1699543372773,
  "repoUrl": "https://github.com/OpenTrafficCam/OTAnalytics",
  "entries": {
    "Python Benchmark with pytest-benchmark": [
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "9659788956b52cf8272517506e8ec7c3feaba306",
          "message": "Merge pull request #380 from OpenTrafficCam/feature/3266-calculate-geometry-once-per-used-offset-group-section-by-offset-before-creating-intersection-objects\n\nFeature/3266 calculate geometry once per used offset group section by offset before creating intersection objects",
          "timestamp": "2023-11-09T11:59:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/9659788956b52cf8272517506e8ec7c3feaba306"
        },
        "date": 1699543372116,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min_with_python_parser",
            "value": 0.11278263460562327,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.866613229038194 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min_with_pandas_parser",
            "value": 0.14460412092266592,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.915432240930386 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hour_with_python_parser",
            "value": 0.01557603139881485,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.2012059680419 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hour_with_pandas_parser",
            "value": 0.020048324726889916,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.87947938905563 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_python_15min",
            "value": 0.07498910488595784,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.335270523908548 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_pandas_15min",
            "value": 0.0037574950816056584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 266.13474622904323 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_python_2hours",
            "value": 0.00826103979380314,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.05013714497909 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_pandas_2hours",
            "value": 0.00020562804686179528,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4863.149824460037 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_python_15min",
            "value": 0.022740165919708313,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 43.975052931928076 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_python_2hours",
            "value": 0.0031769846623559204,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 314.76387401204556 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_pandas_15min",
            "value": 0.002002274067550891,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 499.43212880101055 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_pandas_2hours",
            "value": 0.0001083949538641109,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9225.521708820947 sec\nrounds: 1"
          }
        ]
      }
    ]
  }
}