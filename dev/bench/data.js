window.BENCHMARK_DATA = {
  "lastUpdate": 1705714110012,
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
          "id": "b2306fa31728e319fd5ef66c3cabfb876b1c5166",
          "message": "Merge pull request #402 from OpenTrafficCam/refactor-benchmarks\n\nRefactor benchmarks",
          "timestamp": "2023-11-13T08:50:50Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b2306fa31728e319fd5ef66c3cabfb876b1c5166"
        },
        "date": 1699866688831,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10896155903642323,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.177548567065969 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015071643049951297,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 66.34976669005118 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07317553299319518,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.665769952000119 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008371797570591404,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 119.44865980907343 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0438654383564715,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.796990921953693 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007155876671273665,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 139.7452815270517 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "b2306fa31728e319fd5ef66c3cabfb876b1c5166",
          "message": "Merge pull request #402 from OpenTrafficCam/refactor-benchmarks\n\nRefactor benchmarks",
          "timestamp": "2023-11-13T08:50:50Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b2306fa31728e319fd5ef66c3cabfb876b1c5166"
        },
        "date": 1699873819934,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10754466996749179,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.298461748985574 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01475974844384672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.7518322080141 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07288492408483045,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.720258511020802 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008260735341250464,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.0545984939672 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.04347651833649876,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.000921836937778 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00713669761747714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 140.1208308939822 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1699924770695,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10832423045347894,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.231544925947674 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015047205453512945,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 66.45752283302136 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0730781764268295,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.683975831023417 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008374367657046562,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 119.41200111492071 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.04406155703179685,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.695521160960197 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00716615664054625,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 139.54481462796684 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700011261369,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10725226076221686,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.323812783928588 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014868552143194508,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.25604419107549 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0722649605332454,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.837965074926615 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008349346473473322,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 119.7698530270718 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.04351753456492506,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.97924296488054 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00713585123746226,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 140.1374505609274 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700097735625,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10680890759432259,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.362515004817396 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014740604504562937,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.83982296590693 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07157280978115932,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.971786255948246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008183460564535653,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.19769278704189 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.043250997029784306,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.120854284847155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007067673911481407,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 141.48926684004255 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700184128419,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10713745598506387,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.333803857909516 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014595946447376395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.51217244495638 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07066509188054183,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.151258752914146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008146164324423288,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.75716032413766 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.04257074109420285,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.490312226116657 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006959392314274157,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 143.690706722904 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700270476237,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.103781564693934,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.635622694157064 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01434768039175035,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 69.69767744303681 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07015086633821337,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.25499145197682 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007975497114959726,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.3840338208247 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.042149402779142045,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.725128568010405 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006913576716539132,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 144.642931003822 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700357151371,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1128696752953775,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.859775642864406 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015553314727669248,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.29497618414462 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07594142697902634,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.168043316807598 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008659145130836474,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.4848411581479 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.045775800867679704,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.845603595022112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007470950222334942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.85178193403408 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Sebastian Buck",
            "username": "frunika",
            "email": "38660441+frunika@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "39c25dbb44eb14f195904f78b15268cd9b83983e",
          "message": "Merge pull request #405 from OpenTrafficCam/bug/3569-otvision-build-process-crashes-on-building-assets\n\nchange config because of new build to always having a source",
          "timestamp": "2023-11-13T13:04:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/39c25dbb44eb14f195904f78b15268cd9b83983e"
        },
        "date": 1700443331775,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10992687410094147,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.096956573892385 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015242658980111491,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.60535148787312 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07494577266358009,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.342980724060908 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008546964062691115,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 117.0006089489907 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0448362165150249,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.30339840706438 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0073980633751980955,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.17051007598639 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "b5e625c72cb57920bd66df7a1e14121c516db033",
          "message": "Merge pull request #409 from OpenTrafficCam/bug/3633-exported-count-file-is-not-sorted\n\nbug/3633-exported-count-file-is-not-sorted",
          "timestamp": "2023-11-20T12:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b5e625c72cb57920bd66df7a1e14121c516db033"
        },
        "date": 1700529810066,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11120958601459009,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.992030595894903 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015475326239965852,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.6189931309782 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0750506734131822,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.324330809060484 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008661154166713111,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.45805336697958 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.045086220994850344,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.179725378053263 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007390374190442859,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.31114585418254 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "038409bbd89b2efc44415a1c3f60bb2cb5168d83",
          "message": "Merge pull request #390 from OpenTrafficCam/feature/3359-show-only-the-number-of-cut-tracks-and-the-number-of-all-tracks-instead-of-all-cut-track-ids\n\nFeature/3359 show only the number of cut tracks and the number of all tracks instead of all cut track ids",
          "timestamp": "2023-11-21T14:20:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/038409bbd89b2efc44415a1c3f60bb2cb5168d83"
        },
        "date": 1700616263475,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10663605844301281,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.377690948080271 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014527694949145728,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.83404445787892 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07189227288724959,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.909700720803812 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008175410270695231,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.31802036706358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.04313023191197529,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.185592927969992 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007086320437549969,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 141.11696031992324 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "038409bbd89b2efc44415a1c3f60bb2cb5168d83",
          "message": "Merge pull request #390 from OpenTrafficCam/feature/3359-show-only-the-number-of-cut-tracks-and-the-number-of-all-tracks-instead-of-all-cut-track-ids\n\nFeature/3359 show only the number of cut tracks and the number of all tracks instead of all cut track ids",
          "timestamp": "2023-11-21T14:20:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/038409bbd89b2efc44415a1c3f60bb2cb5168d83"
        },
        "date": 1700702496244,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10790833085796081,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.2671250870917 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014994211847852294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 66.6924017178826 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07305626286204381,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.688080403022468 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008353276105377066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 119.71350969187915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.043651833015732396,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.90854543587193 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007118129938928541,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 140.4863368018996 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "c2ec46bf409c9d42f9946fc99456c5a4079aa146",
          "message": "Merge pull request #383 from OpenTrafficCam/feature/3419-remove-only-events-of-changed-or-deleted-sections\n\nfeature/3419-remove-only-events-of-changed-or-deleted-sections",
          "timestamp": "2023-11-23T14:52:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c2ec46bf409c9d42f9946fc99456c5a4079aa146"
        },
        "date": 1700788796279,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1100107186195707,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.090023340890184 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01510632715657941,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 66.19742771587335 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07381057287087034,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.548194535076618 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008407437725406001,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 118.94230235903524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.056132770988325566,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.814905310980976 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007125431075162679,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 140.34238622919656 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "c2ec46bf409c9d42f9946fc99456c5a4079aa146",
          "message": "Merge pull request #383 from OpenTrafficCam/feature/3419-remove-only-events-of-changed-or-deleted-sections\n\nfeature/3419-remove-only-events-of-changed-or-deleted-sections",
          "timestamp": "2023-11-23T14:52:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c2ec46bf409c9d42f9946fc99456c5a4079aa146"
        },
        "date": 1700875104668,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11452910600507385,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.731404923004447 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015832724170735973,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.16032473099767 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07696575390669724,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.992791589000262 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.0088216598845291,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.35735146100342 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05925294112958947,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.87679937799112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007507591500885507,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.19850978600152 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "c2ec46bf409c9d42f9946fc99456c5a4079aa146",
          "message": "Merge pull request #383 from OpenTrafficCam/feature/3419-remove-only-events-of-changed-or-deleted-sections\n\nfeature/3419-remove-only-events-of-changed-or-deleted-sections",
          "timestamp": "2023-11-23T14:52:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c2ec46bf409c9d42f9946fc99456c5a4079aa146"
        },
        "date": 1700961914822,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11058784265297973,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.042585296992911 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015250505167790132,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.57159838298685 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07451953443551257,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.419300154986558 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008468357733629785,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 118.08665049998672 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.056582670565507615,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.6732556099887 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0071566319868253386,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 139.7305327199865 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "c2ec46bf409c9d42f9946fc99456c5a4079aa146",
          "message": "Merge pull request #383 from OpenTrafficCam/feature/3419-remove-only-events-of-changed-or-deleted-sections\n\nfeature/3419-remove-only-events-of-changed-or-deleted-sections",
          "timestamp": "2023-11-23T14:52:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c2ec46bf409c9d42f9946fc99456c5a4079aa146"
        },
        "date": 1701048112343,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10758439116501575,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.295028666994767 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014846682425939423,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.35511485399911 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07363830740597442,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.579888447013218 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00831934358817399,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 120.20179109100718 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05708321093817018,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.518285736994585 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007184344416656174,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 139.19154511601664 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "65451c0d16d2cea259049faf90a75c3526f835a4",
          "message": "Merge pull request #411 from OpenTrafficCam/bug/3670-background-image-is-not-updated-when-video-is-added\n\nbug/3670-background-image-is-not-updated-when-video-is-added",
          "timestamp": "2023-11-27T12:09:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/65451c0d16d2cea259049faf90a75c3526f835a4"
        },
        "date": 1701134555819,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10765531984178749,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.288904640008695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014891125815963998,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.15408978197956 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07249292927411234,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.794448782980908 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008273797216102437,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 120.86348914302653 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05582761122163341,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.91228351200698 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007072457630994677,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 141.3935653170338 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701307318639,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10517606363403917,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.507866765954532 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014511726330325153,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.90978903800715 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07162030197995005,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.962521412991919 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008116874987493514,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.20012338995002 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05433862837030139,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.403114506043494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006905966395943201,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 144.8023263749783 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701394089038,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10699977164392002,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.34581433807034 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014878754675520828,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.20992595201824 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07214441174957663,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.861087445984595 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008243430025629923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.30872669396922 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.055081551372577815,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.154898964916356 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007063863029643549,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 141.56559885200113 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701479929564,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10848772934427194,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.217632316984236 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014817703018711756,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.48684318596497 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0716070196094962,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.965111318044364 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008217991798526846,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.68422949500382 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05582834324000812,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.912048647063784 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007040584960550832,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 142.03365282900631 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701566706213,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1111176529162956,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.99947014497593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015401977845137693,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.92672629805747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07553063936221073,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.239660202059895 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00863128095955814,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.85765828797594 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05866142844405191,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.046976633952 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0073883004168133195,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.34912545303814 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701652921445,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11460081123316487,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.725941721000709 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015784275707147907,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.35418986296281 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07751482969995414,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.9007572340779 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008805843678004768,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.56095299508888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05976195627751745,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.7330533049535 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007550731962467441,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.43749148701318 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701739351389,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11525224973623197,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.676620215992443 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01568153213725846,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.76927912700921 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07634658735972828,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.0981624010019 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008648116796161655,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.63211084797513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05997717125994798,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.673010397003964 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007541968419484595,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.59137991303578 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "89a11f5c4a501b43e7939008ed150ac7fe8ab1af",
          "message": "Merge pull request #413 from OpenTrafficCam/feature/3728-run-mypy-on-all-files-during-pre-commit-check\n\nfeature/3728-run-mypy-on-all-files-during-pre-commit-check",
          "timestamp": "2023-11-29T07:24:53Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/89a11f5c4a501b43e7939008ed150ac7fe8ab1af"
        },
        "date": 1701825721086,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11582197564740067,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.633940099971369 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.016025085895607978,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 62.40216161799617 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07872616426435594,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.702257366967387 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008927637633862832,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 112.01171474601142 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.060546371248670405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.516266447957605 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007653466081068067,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 130.65975460107438 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "ddd28d840519b8f97ea4012712d439c069167b23",
          "message": "Merge pull request #414 from OpenTrafficCam/bug/3606-selecting-multiple-flows-when-filtering-for-tracks-assigned-to-flows-shows-wrong-tracks\n\nbug/3606-selecting-multiple-flows-when-filtering-for-tracks-assigned-to-flows-shows-wrong-tracks",
          "timestamp": "2023-12-06T18:20:49Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/ddd28d840519b8f97ea4012712d439c069167b23"
        },
        "date": 1701912109746,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11342912820670618,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.81607763199645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015646042946706913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.91392401300254 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0759069372284241,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.174026465996576 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008713512134411856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 114.76428615400073 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05998659165306743,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.67039203999957 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007552179715541021,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.4121032160001 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "id": "646fe222dc9d16a46e71d9d4488aba54b663392f",
          "message": "Merge branch 'main' into feature/2485-reimplement-intersection-strategy-for-sections-and-flows",
          "timestamp": "2023-12-06T17:09:27Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/646fe222dc9d16a46e71d9d4488aba54b663392f"
        },
        "date": 1701961214784,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11380540205884274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.786929108013283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015402825656526615,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.92315256300208 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.012754538007162888,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 78.40346702000534 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.0017164042264769283,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 582.6133404790016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.35920958991656754,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7838900409988128 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.05307844116422177,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.840040853989194 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "id": "779302e5767c62b9116b42ca693635af9fa00407",
          "message": "Switch to pandas track store implementation in benchmark",
          "timestamp": "2023-12-07T15:21:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/779302e5767c62b9116b42ca693635af9fa00407"
        },
        "date": 1701967360319,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14534049196098384,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.88039504000335 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020487786186812268,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.80956833899836 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.003844228979817033,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 260.13018611799635 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.0004548989217519549,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2198.2905480379995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.006696551560982425,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 149.33059066199348 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0008841386447807302,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1131.0443287410017 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8ecf8eefb2af7bdb9a552e5a99430420dc6b7416",
          "message": "Merge pull request #417 from OpenTrafficCam/bug/3568-stracktrace-isnt-logged-on-cli\n\nbug/3568-stracktrace-isnt-logged-on-cli",
          "timestamp": "2023-12-07T19:33:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8ecf8eefb2af7bdb9a552e5a99430420dc6b7416"
        },
        "date": 1701998543317,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11090010568193495,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.017123958998127 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01569801816764778,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.70230874499248 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07629465755392624,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.107077638996998 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00871001417111529,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 114.81037577599636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05904579734405716,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.936006371004623 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007483859051775135,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.6209024090058 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8ecf8eefb2af7bdb9a552e5a99430420dc6b7416",
          "message": "Merge pull request #417 from OpenTrafficCam/bug/3568-stracktrace-isnt-logged-on-cli\n\nbug/3568-stracktrace-isnt-logged-on-cli",
          "timestamp": "2023-12-07T19:33:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8ecf8eefb2af7bdb9a552e5a99430420dc6b7416"
        },
        "date": 1702084805575,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1127247927721223,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.871162903989898 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01578232560205827,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.3620180709986 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07669518986824729,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.038627347006695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008747537662621485,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 114.31788447999861 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.059007323506961945,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.947048952017212 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007495903918922988,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.4061923440022 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8ecf8eefb2af7bdb9a552e5a99430420dc6b7416",
          "message": "Merge pull request #417 from OpenTrafficCam/bug/3568-stracktrace-isnt-logged-on-cli\n\nbug/3568-stracktrace-isnt-logged-on-cli",
          "timestamp": "2023-12-07T19:33:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8ecf8eefb2af7bdb9a552e5a99430420dc6b7416"
        },
        "date": 1702171553228,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11318298667519325,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.835250150004867 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015557574602031797,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.27737134999188 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07598346506098608,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.16075805699802 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008622346279274006,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.97771274899424 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05897258025291318,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.957033179001883 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007445749010654166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 134.30482259999553 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8ecf8eefb2af7bdb9a552e5a99430420dc6b7416",
          "message": "Merge pull request #417 from OpenTrafficCam/bug/3568-stracktrace-isnt-logged-on-cli\n\nbug/3568-stracktrace-isnt-logged-on-cli",
          "timestamp": "2023-12-07T19:33:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8ecf8eefb2af7bdb9a552e5a99430420dc6b7416"
        },
        "date": 1702257774164,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10516467887764752,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.508896054001525 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014525848406116086,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.84279472302296 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0715937477624007,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.967700131004676 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008155374975109864,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.61851883598138 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05478733516345126,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.252393495989963 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006979556809879166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 143.27557282499038 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "id": "33901fee853fee53f441577459a181641efa69b6",
          "message": "Merge branch 'main' into feature/2485-reimplement-intersection-strategy-for-sections-and-flows",
          "timestamp": "2023-12-11T12:25:17Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/33901fee853fee53f441577459a181641efa69b6"
        },
        "date": 1702300329360,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13825403918746546,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.233061730978079 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019472641091563027,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.35410216302262 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.037900383298991404,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.384957431990188 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.004554103415810385,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.58218966401182 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.006586743123065111,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 151.82010005798656 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0008815636301771782,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1134.3480671939906 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "8ecf8eefb2af7bdb9a552e5a99430420dc6b7416",
          "message": "Merge pull request #417 from OpenTrafficCam/bug/3568-stracktrace-isnt-logged-on-cli\n\nbug/3568-stracktrace-isnt-logged-on-cli",
          "timestamp": "2023-12-07T19:33:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8ecf8eefb2af7bdb9a552e5a99430420dc6b7416"
        },
        "date": 1702344161445,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10959852120578206,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.124210701003904 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015158565576527663,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.96930263299146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0730664342340891,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.68617492399062 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008447395144883628,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 118.37968780301162 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05683352173137349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.59524959101691 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007217767688380582,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 138.54699169797823 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "e4dfa4ae1dedeafe0dc4c2618092614f5a05fac6",
          "message": "Merge pull request #420 from OpenTrafficCam/bug/3817-wrong-title-for-export-eventlist-popup\n\nbug/3817-wrong-title-for-export-eventlist-popup",
          "timestamp": "2023-12-12T10:04:33Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/e4dfa4ae1dedeafe0dc4c2618092614f5a05fac6"
        },
        "date": 1702430561325,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10422329264720957,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.594784184999298 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014366090404556083,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 69.60836051002843 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.06985960781971488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.314423330011778 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008115752951844427,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.21715630497783 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.054590071803182344,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.318349234003108 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006928047029913253,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 144.340821544989 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702516900266,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10320734575507863,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.689232802993502 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014433450252446892,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 69.28350342500198 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0713118105992819,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.022922592994291 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008198267673092422,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.97698829499132 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05404104837469345,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.50445226499869 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0068845818583299625,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.2521039879939 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "id": "635b35f2738a9ec1666103a8de6d98bd08eefcbf",
          "message": "Add vectorized projections calculation",
          "timestamp": "2023-12-14T12:58:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/635b35f2738a9ec1666103a8de6d98bd08eefcbf"
        },
        "date": 1702561506597,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12569846899682457,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.955546380006126 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.017498159502723536,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.14886756200576 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.11898590287291819,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.404356951999944 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.015625756276346107,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 63.99690244201338 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.006272575488955238,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 159.42414750700118 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0008396464566510056,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1190.9774549499998 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702603412587,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10808955254420537,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.251587932987604 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014846337351620697,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.35668039301527 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07053220161889819,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.177921247988706 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008157566892973101,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.58557154602022 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05395535679509209,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.53384092700435 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006824226471635672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.5367546280031 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702689713329,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10757582831748846,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.295768534997478 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014741691928372335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.83481874800054 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07106803854306054,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.071022930991603 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008155337328215044,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.61908487099572 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05422773465139672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.440748196997447 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006824619967334416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.52830557400011 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702776416446,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10744909534583892,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.306732614000794 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01473705109745747,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.8561805470381 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07115068965052357,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.054677542997524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008109680494474643,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.30942022701493 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05406296360133958,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.4969512099633 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006856474831882241,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.84754185198108 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702862614892,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10481262288710443,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.540835564024746 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014533934928543976,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.80449134501396 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.06998272073001843,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.28924153803382 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007970058432167786,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.46959454700118 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05362049668207599,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.649584802042227 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006799649521612019,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 147.06640347000211 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "bd481fba9497ce3cd8d39fc5e1cea1c776aa9528",
          "message": "Merge pull request #415 from OpenTrafficCam/feature/1963-resolve-merge-conflicts-of-different-track-files-automatically\n\nfeature/1963-resolve-merge-conflicts-of-different-track-files-automatically",
          "timestamp": "2023-12-13T09:17:07Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bd481fba9497ce3cd8d39fc5e1cea1c776aa9528"
        },
        "date": 1702948941378,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10503219730056114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.520890028972644 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01437368616991681,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 69.57157601596555 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.06957162647932999,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.373675744049251 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007918240227446334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 126.29068723297678 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.053606364143290244,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.654501494020224 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006786967833479841,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 147.34120221802732 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703034594229,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10665655861726761,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.375888486974873 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014607840390297106,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.45638871192932 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07105433212829171,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.073737238068134 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007983325729287246,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.26107964396942 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.053768281008597436,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.598325653001666 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006847168835474972,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.0457634429913 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703121655232,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10650166060557437,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.389524954953231 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014772109008530909,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.69514085107949 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07085557509084325,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.113215491059236 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008130933373117726,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.98711034900043 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05430875313193631,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.413238057051785 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0068831852267288674,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.28157634299714 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "id": "a856daaf3a71ad8a8c16a06c594e1ae34de0b907",
          "message": "Reduce number of generated flyweights to create scene events",
          "timestamp": "2023-12-21T10:32:16Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a856daaf3a71ad8a8c16a06c594e1ae34de0b907"
        },
        "date": 1703156853631,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12513315334320768,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.991487254039384 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.017661852354808657,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.61920278298203 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.11918650373262525,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.390211715945043 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.015265524702270621,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.50708341202699 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.01131523789998381,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 88.37640081800055 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0015378621036762742,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 650.2533599140588 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703208035878,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10775700181578614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.280139416921884 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014748648775786705,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.80282147892285 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07158278978481833,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.969838322955184 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00812142906182113,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.13103917893022 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.054267064490848074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.427383337984793 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0068829849887560406,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.28580283606425 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "id": "def5dd58da4f540ce223b264572e12e979923d65",
          "message": "Change creation of events",
          "timestamp": "2023-12-22T09:47:39Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/def5dd58da4f540ce223b264572e12e979923d65"
        },
        "date": 1703240463465,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1280353688344841,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.81034185399767 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.017842361498362744,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.046392743010074 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.12174684087911017,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.213765488937497 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.015498384130990197,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.52285551500972 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.011713675345842185,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 85.37030184594914 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0016066270634612634,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 622.421981269028 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "id": "27b981409105587a549b75232e2e94338976591b",
          "message": "Remove iterrows over dataframe",
          "timestamp": "2023-12-22T22:14:38Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27b981409105587a549b75232e2e94338976591b"
        },
        "date": 1703284627925,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12678433528448016,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.887409732094966 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01757507313750462,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.89876748598181 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.12010730300480801,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.325888392981142 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.015528583472175088,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 64.39737415791024 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.22731185653063185,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.399242587969638 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.029971888345974546,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 33.364597801002674 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703294310762,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10739631400546426,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.311306530958973 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014781197261214723,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.6535183400847 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.06993669376637761,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.29864562000148 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007998150009793752,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.02891278301831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0545180310062491,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.342555326060392 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006877622461384335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.39908313006163 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703381125658,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10673578494596021,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.368929085088894 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014635670317474427,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.32621795299929 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07077668601768411,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.128946356009692 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00796160191934335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.60286361095496 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05438098958276025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.388779013999738 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006870565441998637,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.5484280649107 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703467339460,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10583960183352356,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.448259277967736 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014643010091410374,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.29196959896944 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07089364056712387,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.105637572007254 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00801955119014493,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 124.69525741401594 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05439466375933699,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.38415629195515 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006841507887999361,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.16660776699428 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703553558125,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10679550425078954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.363690044963732 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014670463103251282,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.16417402517982 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07203209966530984,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.882699583191425 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008246668339192614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 121.26109100901522 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05463858180481073,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.302085577044636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006956020568378153,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 143.76035696989857 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703639986626,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10617519362170949,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.418395821936429 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014674803411640932,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.14401337783784 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07114942229616548,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.05492789298296 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008106925958667122,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.35131776193157 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05431336262306714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.41167535400018 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00688933310662058,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.1519304588437 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703726387152,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10820808481075034,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.241453646915033 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014809440062455057,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.52449760306627 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0711599625365867,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.052846071776003 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008092182549776356,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 123.57605551392771 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05411999665137336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.47745864512399 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006841387058167279,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.16918930294923 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703812269568,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10460901344355443,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.55940570589155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014508700528956336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.92416023090482 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07015970851387923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.25319490605034 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007968542467101656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.49346434790641 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.053763101279714134,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.600117482012138 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006838189992515107,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.23752792691812 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703899149136,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10800818611597209,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.25855748495087 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014766291957118777,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.72180875902995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07125206905562811,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.034680160926655 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008022521223021436,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 124.6490937450435 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05366496366103768,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.634131690021604 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006881128981843227,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.32498993095942 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1703985951558,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10812538244300342,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.248522200854495 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01488371082268427,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.18754562712274 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07193214127221832,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.901991270016879 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008143189975856212,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.8019981069956 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05506240889154055,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.16121052694507 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00699199836203899,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 143.02062846999615 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704072463725,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1051708505335581,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.508338051149622 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014463078126048808,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 69.14157493202947 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07046312343383913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.191820505075157 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.007959411775969935,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 125.63742499402724 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05381773630719185,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.581234897952527 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006839108685392263,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.21788393799216 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704158406055,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10770374300993905,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.284728385973722 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014819918585968584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.47675395105034 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07089694915644865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.104979295982048 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.0081405701484104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 122.84151868592016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.054467439384741786,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.359592653810978 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006887800905858145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 145.18421970494092 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704244906625,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10518792400293386,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.506794715067372 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.014561821944562334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 68.67272541904822 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07004866029443282,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.275790511863306 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008008136161529247,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 124.87300163600594 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05359706165159438,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.657739233924076 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006818059695516879,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 146.66929370793514 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704331313919,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.10730341852099223,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.31936758197844 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01488962301437097,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 67.1608676079195 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07112025736588519,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.060691524995491 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008049370415937259,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 124.23331867298111 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.053249638400242806,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.779470246983692 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.006920722366430249,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 144.49358709296212 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704417703745,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11008793587976971,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.08364746789448 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015198062946980218,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.79785881191492 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07327274411914111,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.647639542119578 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008349630110355692,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 119.76578444591723 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.055289759191737196,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.086532020010054 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.00707513041371515,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 141.3401508559473 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704504055642,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11057266611218376,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.043826428001921 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015164199987342966,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 65.94479107599909 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07326209420431792,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.649623463003081 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008452338105307749,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 118.31045889799861 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05608806895954715,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.829103739000857 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007112261724695394,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 140.60224984800152 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704590831765,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11682792784788411,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.559597165003652 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.016080029725459504,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 62.18893976400432 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07823491127953668,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.782017434990848 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008847508775296104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.02616650600976 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.05996859681344539,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.675394341989886 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007573055341684422,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.0471005270083 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704676969911,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11521071178115597,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.679748475988163 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01596570499664075,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 62.63425261899829 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07799071360900356,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.822039365011733 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008841732680170744,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.10000383100123 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0596446385734451,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.765966295002727 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007507924669107954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.19259903000784 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704763355820,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1163782563842324,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.59267040999839 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01602556433381807,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 62.40029862098163 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07778737259956066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.855556969996542 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.00877907866266018,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.9071693540318 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0593509851992378,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.848919973999728 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007536929969321566,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.6800174700329 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "73cf99ec1562cd57363f7f8aa5750644e9f284d0",
          "message": "Merge pull request #423 from OpenTrafficCam/bug/3863-cutting-uses-gui-offset-instead-of-section-offset\n\nbug/3863-cutting-uses-gui-offset-instead-of-section-offset",
          "timestamp": "2023-12-19T11:51:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/73cf99ec1562cd57363f7f8aa5750644e9f284d0"
        },
        "date": 1704849766357,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11482691061428643,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.708759947039653 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.015922356817891788,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 62.80477265000809 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07609821740191698,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.140912286005914 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.008638394942511276,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.76224595599342 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.057734069373953194,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.32079534395598 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.007358980241410451,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.88839311903575 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "id": "c3da16b453afe8dca167d67b1214031291ee8730",
          "message": "Remove resolved todo comment",
          "timestamp": "2024-01-10T15:49:59Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c3da16b453afe8dca167d67b1214031291ee8730"
        },
        "date": 1704908342241,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13649975293670036,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.326020586013328 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019257621591321567,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.92749246099265 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1307486482235873,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.6482626289944164 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01690900749346466,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.140076695010066 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.24671767520259222,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.053215884021483 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.032674495513205,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.60491016902961 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "a55e8a51db8e77b96c1422a4ea181e0d2caa44ed",
          "message": "Merge pull request #416 from OpenTrafficCam/feature/2485-reimplement-intersection-strategy-for-sections-and-flows\n\nFeature/2485 reimplement intersection strategy for sections and flows",
          "timestamp": "2024-01-10T18:58:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a55e8a51db8e77b96c1422a4ea181e0d2caa44ed"
        },
        "date": 1704936586859,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13720893787065208,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.288154951995239 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019473751762147648,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.351173220959026 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13042530062704233,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.6672240369953215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017098789117033303,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 58.4836735019926 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.2475253102643537,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.03999089600984 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03286100611428521,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.431204587046523 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Lars Briem",
            "username": "briemla",
            "email": "lars.briem@platomo.de"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "a55e8a51db8e77b96c1422a4ea181e0d2caa44ed",
          "message": "Merge pull request #416 from OpenTrafficCam/feature/2485-reimplement-intersection-strategy-for-sections-and-flows\n\nFeature/2485 reimplement intersection strategy for sections and flows",
          "timestamp": "2024-01-10T18:58:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a55e8a51db8e77b96c1422a4ea181e0d2caa44ed"
        },
        "date": 1705023796039,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13751271291939068,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.272054916014895 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01914498424946777,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 52.233001969056204 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1294882630957218,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.722707650042139 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01680771772544601,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.49647753103636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.24395930640843977,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.099044282105751 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.032683771873033056,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.596223835018463 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "committer": {
            "name": "Randy Seng",
            "username": "randy-seng",
            "email": "19281702+randy-seng@users.noreply.github.com"
          },
          "id": "c36ae4cfbcd988831561ae36d94446aa5b789406",
          "message": "Change to PythonTrackDataset",
          "timestamp": "2024-01-12T10:42:17Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c36ae4cfbcd988831561ae36d94446aa5b789406"
        },
        "date": 1705057378567,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13743942773478304,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.275932507007383 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019217484695091873,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 52.03594621596858 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13095266030856834,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.636347346007824 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.016931794667727332,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.06048470491078 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25175820503795754,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.9720651799580082 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.032986665143806077,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.315280300099403 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705109339097,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13748123927406838,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2737197109963745 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019032887956695464,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 52.54063399496954 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1308694898643419,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.641200412996113 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01683652104805974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.39469306904357 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.24880954119994525,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.01913847506512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03267450228725539,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.604903824045323 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705196079092,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13809437548118494,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.241424544015899 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019353816468789867,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.66939562605694 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1316542084319299,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.595655406010337 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.016843043025646535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.371694204979576 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25237515125532,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.962355228024535 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03312574928733694,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.18799639295321 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705282322542,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13668759248802656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.315952982986346 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019185492202661688,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 52.12271801196039 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13239608997258018,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.553093148046173 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.016904254496321394,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.156705208006315 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.2437613715245958,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.1023727169958875 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.032754642470401586,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.530023367027752 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705368553775,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13921819840021066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.1829689759761095 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019317804116069422,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.76571798697114 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1326981072461366,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.535902514006011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017207103216114968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 58.1155344650615 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25413737798803976,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.934879662003368 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03316663148435516,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.150785751990043 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705455075189,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13816282705600624,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.237836843007244 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01951562707158308,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.24098735500593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1341147841823395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.456299513112754 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017275032745340976,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.88701038900763 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25626193207245995,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.9022573189577088 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03365445789286466,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.71374559600372 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705541337208,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14199035982471817,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.042731642024592 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019837944624720612,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.408447997877374 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13351168949761236,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.489980868063867 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01725284074187876,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.9614693580661 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.2512124830061898,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.980693905148655 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03367367572542027,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.696787726832554 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705627778645,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14233644531772258,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.025607515824959 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02004661082430483,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.88374387891963 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13641600707975285,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.330518033821136 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017520089296245114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.07733465800993 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25937403774462164,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.855435990029946 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.033865057988481925,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.528961690841243 sec\nrounds: 1"
          }
        ]
      },
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
          "id": "27cb19348658af79a40723966540e6b65a5dc7fa",
          "message": "Merge pull request #430 from OpenTrafficCam/bug/4010-export-of-events-fails\n\nbug/4010-export-of-events-fails",
          "timestamp": "2024-01-12T09:53:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/27cb19348658af79a40723966540e6b65a5dc7fa"
        },
        "date": 1705714109252,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1411536865954971,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.084476673044264 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019944831079838996,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.13830380397849 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13561365204882161,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.373888873960823 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017600893213556647,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.815298398025334 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.2575956876569687,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.8820525649935007 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.0338854498662654,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.511191498022527 sec\nrounds: 1"
          }
        ]
      }
    ]
  }
}