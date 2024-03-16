window.BENCHMARK_DATA = {
  "lastUpdate": 1710552130961,
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
        "date": 1705800867499,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1418800001166114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.0482097489293665 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.0198346922429398,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.41671369294636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1349656263531664,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.40929395891726 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017348089247383684,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.64323584805243 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25816947738180374,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.8734245819505304 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03393304296655773,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.469800306018442 sec\nrounds: 1"
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
        "date": 1705887140057,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13605467253797654,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.349986452842131 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019196137659309304,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 52.09381271107122 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13413122062255078,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.455385818146169 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01752462103715128,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.062574869953096 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25810925935750345,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.874328268924728 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.033738609033170136,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.6396333060693 sec\nrounds: 1"
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
        "date": 1705974424326,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13417722737543578,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.452829511836171 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019637261955815048,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.92359628598206 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13433275221158383,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.444200937869027 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01738124707970937,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.53327108314261 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25353896551871313,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.944166917121038 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03375283879135206,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 29.627137621864676 sec\nrounds: 1"
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
          "id": "212a2a063f376d1786479a09f7bb8fb409a42de5",
          "message": "Merge pull request #428 from OpenTrafficCam/feature/3027-get-metadata-for-tracks-in-trackdataset\n\nfeature/3027-get-metadata-for-tracks-in-trackdataset",
          "timestamp": "2024-01-23T08:13:11Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/212a2a063f376d1786479a09f7bb8fb409a42de5"
        },
        "date": 1705999544946,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13617460488221003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.343513137893751 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019400643973517966,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.54468075209297 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.132479467077685,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.548339543165639 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017049961931751408,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 58.65115734585561 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.25086498421863973,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.9862079720478505 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.03314582917424675,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 30.169708373956382 sec\nrounds: 1"
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
          "id": "971ce1877a7d7e522a107a15b723efddd4ae319b",
          "message": "Merge remote-tracking branch 'origin/main' into feature/3995-pandas-implementation-to-cut-tracks-with-sections\n\n# Conflicts:\n#\tOTAnalytics/application/state.py\n#\tOTAnalytics/domain/track_dataset.py\n#\tOTAnalytics/plugin_datastore/python_track_store.py\n#\tOTAnalytics/plugin_datastore/track_store.py\n#\ttests/OTAnalytics/plugin_datastore/test_python_track_storage.py\n#\ttests/OTAnalytics/plugin_datastore/test_track_store.py",
          "timestamp": "2024-01-23T08:33:35Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/971ce1877a7d7e522a107a15b723efddd4ae319b"
        },
        "date": 1706004582507,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13740688579596053,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.277655659010634 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019516578255245838,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 51.2384900120087 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13503123254297844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.405694084009156 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01754506627440383,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.996079944074154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1349220024401003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.411689582979307 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017258496089819657,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.9424762618728 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13208938085035304,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.5706312919501215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.016926343373188234,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 59.07950571202673 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.04729183159245032,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.145300706848502 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.006334117225536665,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 157.87519624177366 sec\nrounds: 1"
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
          "id": "d68a4d6fcc5c8898c0b2528ac215f7e0405755cf",
          "message": "Merge pull request #432 from OpenTrafficCam/feature/3995-pandas-implementation-to-cut-tracks-with-sections\n\nFeature/3995 pandas implementation to cut tracks with sections",
          "timestamp": "2024-01-23T10:15:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/d68a4d6fcc5c8898c0b2528ac215f7e0405755cf"
        },
        "date": 1706005732170,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14015791228469654,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.134809470968321 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019931512272727308,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.171807653969154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13630751054342757,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.336352898040786 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017877544275175954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.936094164149836 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13694829315522802,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.302026019897312 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017567040664482076,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.92478426499292 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13597073845765564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.354523563990369 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017185237937708,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 58.18947655102238 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.350773029144292,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.850846322020516 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.041059428772972154,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 24.35494184610434 sec\nrounds: 1"
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
          "id": "92dec9cde92a563861d5f7d1f3f4c800c90ba524",
          "message": "Merge pull request #434 from OpenTrafficCam/dependabot/pip/pillow-10.2.0\n\nBump pillow from 10.1.0 to 10.2.0",
          "timestamp": "2024-01-23T14:32:09Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/92dec9cde92a563861d5f7d1f3f4c800c90ba524"
        },
        "date": 1706059431436,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14533821849813225,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.880502667045221 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019885720954469003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.2873394577764 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13805176341647832,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.243659734958783 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017976884689014653,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.62699084402993 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14135140890561101,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.074566909112036 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018215223482228246,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.899134285980836 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.14046267171865087,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.119329198030755 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017985182043468193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.60132766980678 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.37044009928858335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.6994917718693614 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.042876985798276465,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.322534953942522 sec\nrounds: 1"
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
          "id": "a5c75c6ad0473dc3e911028e28ba541a180b6556",
          "message": "Merge pull request #436 from OpenTrafficCam/feature/4096-print-overall-processing-time-after-otanalytics-has-been-closed\n\nfeature/4096-print-overall-processing-time-after-otanalytics-has-been-closed",
          "timestamp": "2024-01-24T08:16:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a5c75c6ad0473dc3e911028e28ba541a180b6556"
        },
        "date": 1706145811511,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1419294316878489,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.045754979131743 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019833129201953407,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.420687014004216 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13911772773273448,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.188156508142129 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017836351627484877,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.06527729914524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14027430537970817,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.128889337880537 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018159248520979065,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.06835807906464 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13652693907117774,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.32456178101711 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017766032142840928,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.28718849318102 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36216173743823155,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7611972680315375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.042334243993037694,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.621539105894044 sec\nrounds: 1"
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
          "id": "a5c75c6ad0473dc3e911028e28ba541a180b6556",
          "message": "Merge pull request #436 from OpenTrafficCam/feature/4096-print-overall-processing-time-after-otanalytics-has-been-closed\n\nfeature/4096-print-overall-processing-time-after-otanalytics-has-been-closed",
          "timestamp": "2024-01-24T08:16:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a5c75c6ad0473dc3e911028e28ba541a180b6556"
        },
        "date": 1706231886193,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14012052960308913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.136712962994352 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019751647304368573,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.62868856405839 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13782845311681563,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.255395946092904 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017749845683070673,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.33851797110401 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13884279481868703,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2023903098888695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018313266984438824,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.60522149596363 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13747423664615815,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2740902178920805 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017794296411365727,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.19778252998367 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3655679365953816,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.735469662118703 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04235311576342798,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.611013781977817 sec\nrounds: 1"
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
          "id": "a5c75c6ad0473dc3e911028e28ba541a180b6556",
          "message": "Merge pull request #436 from OpenTrafficCam/feature/4096-print-overall-processing-time-after-otanalytics-has-been-closed\n\nfeature/4096-print-overall-processing-time-after-otanalytics-has-been-closed",
          "timestamp": "2024-01-24T08:16:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a5c75c6ad0473dc3e911028e28ba541a180b6556"
        },
        "date": 1706318153087,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1433511198394541,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.9758785360027105 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020116419577168112,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.7106354420539 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13840742538066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.225045890780166 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.018050387665671658,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.40047219605185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14261046118696705,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.012108310125768 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01828680231261967,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.68424620688893 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13854980774593575,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.217620986048132 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017923549056915847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.792521716794 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.37075833118467677,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.69717472512275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04274943806719508,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.392120346194133 sec\nrounds: 1"
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
          "id": "a5c75c6ad0473dc3e911028e28ba541a180b6556",
          "message": "Merge pull request #436 from OpenTrafficCam/feature/4096-print-overall-processing-time-after-otanalytics-has-been-closed\n\nfeature/4096-print-overall-processing-time-after-otanalytics-has-been-closed",
          "timestamp": "2024-01-24T08:16:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a5c75c6ad0473dc3e911028e28ba541a180b6556"
        },
        "date": 1706404882101,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14353702669424595,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.966843490008614 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020071179017053787,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.82268351801031 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1387552861646696,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.206932633998804 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01795160416298825,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.7053281099943 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1414066975143382,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.071800823992817 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018267409429226292,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.74229960599041 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13813788777680588,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.239143554994371 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.0178910699998885,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.8938062399975 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3684274830477112,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.714238340005977 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04270348786864238,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.417290950004826 sec\nrounds: 1"
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
          "id": "a5c75c6ad0473dc3e911028e28ba541a180b6556",
          "message": "Merge pull request #436 from OpenTrafficCam/feature/4096-print-overall-processing-time-after-otanalytics-has-been-closed\n\nfeature/4096-print-overall-processing-time-after-otanalytics-has-been-closed",
          "timestamp": "2024-01-24T08:16:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a5c75c6ad0473dc3e911028e28ba541a180b6556"
        },
        "date": 1706491174551,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1454008464372325,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.877539054985391 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020254736880801386,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.37116714401054 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13994145692475074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.145845283987001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.018029514990132486,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.464609033981105 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14222601536105803,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.031062477995874 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018357460068072762,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.47376686599455 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13794036256218614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.249509725981625 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017899111522090883,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.8686948659888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.37004905362125656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7023444330261555 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.043378562869941656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.05286145597347 sec\nrounds: 1"
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
          "id": "49352ddd480a2d2acd8e2a18730898fa68644cec",
          "message": "Merge pull request #438 from OpenTrafficCam/bug/4002-log-stdout-polluted-with-number-of-detections-warnings\n\nbug/4002-log-stdout-polluted-with-number-of-detections-warnings",
          "timestamp": "2024-01-29T08:56:38Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/49352ddd480a2d2acd8e2a18730898fa68644cec"
        },
        "date": 1706577390048,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14377569839456114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.955278334004106 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020067650085707243,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.83144492399879 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13820993557467937,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.235369844012894 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01793486691157009,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.75731366898981 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1407826450971702,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.103148256021086 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01832241152887083,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.577968540019356 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13765680314388834,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2644429999927524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017944665326650993,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.726868224999635 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3570969722206584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.80035978401429 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.0427623583262895,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.385052628989797 sec\nrounds: 1"
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
          "id": "96ef8e09c59ea90215a6486b6e7fc40d17916d21",
          "message": "Merge pull request #445 from OpenTrafficCam/bug/4102-start-and-endpoints-are-plotted-in-reversed-direction\n\nbug/4102-start-and-endpoints-are-plotted-in-reversed-direction",
          "timestamp": "2024-01-30T14:51:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/96ef8e09c59ea90215a6486b6e7fc40d17916d21"
        },
        "date": 1706663875099,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14181710668353817,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.051335508003831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019649560915066238,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.891722431988455 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13824883394196746,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2333340650075115 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017675549578594397,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.575327151978854 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13766434352196114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.26404509996064 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018090003022397348,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.279150520975236 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1368814369506987,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.305592506018002 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017768580587357734,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.27911554800812 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3566846502317519,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.803596957004629 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04165771989717905,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 24.005154446000233 sec\nrounds: 1"
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
          "id": "5cfd511496d91576d9f4cdb72ab9633a2c1c2e5f",
          "message": "Merge pull request #443 from OpenTrafficCam/dependabot/pip/pre-commit-3.6.0\n\nBump pre-commit from 3.5.0 to 3.6.0",
          "timestamp": "2024-01-31T15:18:01Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/5cfd511496d91576d9f4cdb72ab9633a2c1c2e5f"
        },
        "date": 1706750511351,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14435446292593604,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.927392335026525 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02012778454110041,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.68256680003833 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1411912388459767,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.082592434016988 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01795702268498824,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.68851905700285 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14108141201034521,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.088105979026295 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018383769994599845,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.395806752028875 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13928360880839777,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.179595708032139 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017973898328578618,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.636233259981964 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3727195924242143,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.6829821139690466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04364374578076797,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.91279041499365 sec\nrounds: 1"
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
          "id": "9890aea7b87f03a2f50b224074b1717a5cf0cb05",
          "message": "Merge pull request #295 from OpenTrafficCam/user-story/2061-boundingboxes-of-detections-per-frame\n\nUser story/2061 boundingboxes of detections per frame",
          "timestamp": "2024-02-01T11:34:33Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/9890aea7b87f03a2f50b224074b1717a5cf0cb05"
        },
        "date": 1706836604500,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14370877365521934,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.958517385995947 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01994529204846151,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.13714502501534 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1416316350135376,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.060569482971914 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017677678356829603,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.56851424800698 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.14049765822137236,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.117556354030967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.018449119323893044,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 54.203129290021025 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1362346484761235,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.34027658298146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017760478121379788,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.30479051102884 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3484000207942047,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8702638929826207 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04293729454159423,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.2897766539827 sec\nrounds: 1"
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
          "id": "e8ae27176ff243463a2724f0532beb63d279d667",
          "message": "Merge pull request #449 from OpenTrafficCam/task/2578-profile-event-handling\n\ntask/2578-profile-event-handling",
          "timestamp": "2024-02-02T10:06:08Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/e8ae27176ff243463a2724f0532beb63d279d667"
        },
        "date": 1706869250105,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1419225557199542,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.046096337027848 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020374282267144585,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.08148355304729 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13459407323469946,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.429747655056417 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017076863509268923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 58.55876282299869 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13217388304292935,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.565791190951131 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017715654947577507,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.44724978890736 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1327509355087921,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.5329036000184715 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017368024440871564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.57707236101851 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36409744882778755,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.746517459047027 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04249461068122854,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.532395849004388 sec\nrounds: 1"
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
          "id": "e8ae27176ff243463a2724f0532beb63d279d667",
          "message": "Merge pull request #449 from OpenTrafficCam/task/2578-profile-event-handling\n\ntask/2578-profile-event-handling",
          "timestamp": "2024-02-02T10:06:08Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/e8ae27176ff243463a2724f0532beb63d279d667"
        },
        "date": 1706923177465,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1455161032100199,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.8720916650490835 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02022117400114812,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.45311285799835 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1379703877297791,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.247932084952481 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017318177671573867,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.74279597797431 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13732072375637103,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.282222032081336 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01762675968594218,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.73192451801151 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1333199027030578,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.5007555490592495 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.01728654096013543,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.84847311594058 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3447284038032841,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.900834364001639 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04217356492612565,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.71153592900373 sec\nrounds: 1"
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
          "id": "e8ae27176ff243463a2724f0532beb63d279d667",
          "message": "Merge pull request #449 from OpenTrafficCam/task/2578-profile-event-handling\n\ntask/2578-profile-event-handling",
          "timestamp": "2024-02-02T10:06:08Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/e8ae27176ff243463a2724f0532beb63d279d667"
        },
        "date": 1707009730968,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14289548935213037,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.998121525975876 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02059463903972297,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.556325656943955 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1354837084456836,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.380961234914139 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01729296924962025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.8269691899186 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13874049648538797,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.207700890023261 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01770660131226358,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.476112064905465 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1355376666022777,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.37802284094505 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.01740596943800248,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.45155439700466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3672241153285844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.723132709041238 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04250293705283644,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.527785827056505 sec\nrounds: 1"
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
          "id": "e8ae27176ff243463a2724f0532beb63d279d667",
          "message": "Merge pull request #449 from OpenTrafficCam/task/2578-profile-event-handling\n\ntask/2578-profile-event-handling",
          "timestamp": "2024-02-02T10:06:08Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/e8ae27176ff243463a2724f0532beb63d279d667"
        },
        "date": 1707096098129,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14635071737821212,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.832901251967996 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020357544958485903,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.1218367459951 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13746473731488534,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.274592884932645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.0172617427859491,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.931578079937026 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1380511255941923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.243693202035502 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01764985798613741,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.65767967002466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13410000338385436,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.457121362909675 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017346094850076335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.64986347896047 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.350607324370514,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.852193695027381 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04198575341736621,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.81760284397751 sec\nrounds: 1"
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
          "id": "44d54b7b04207351b29cb7dcaf318f2b9ac0b666",
          "message": "Merge pull request #453 from OpenTrafficCam/dependabot/pip/isort-5.13.2\n\nBump isort from 5.12.0 to 5.13.2",
          "timestamp": "2024-02-05T20:16:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/44d54b7b04207351b29cb7dcaf318f2b9ac0b666"
        },
        "date": 1707182203437,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14677721100912616,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.813046747003682 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020598181179359906,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.54797573108226 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13795101591614076,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.248949878034182 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017426397038558774,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.384208438917994 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13920835268585233,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.183477001963183 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017882433735381138,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.920799975981936 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13503986730093176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.405220546992496 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.01763717834964108,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.6984117400134 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36712047862124,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7239014389924705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.042909322630941035,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.304958892054856 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707268480892,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14602804640448538,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.847999576944858 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020437527812667895,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.929597022011876 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13607819246420902,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.348716071923263 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01755862434855807,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.95206982898526 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13816041591433093,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.237963155959733 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01778591589261758,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.224262277944945 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1350403890663579,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.405191934900358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017783069945746362,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.23326023295522 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36315883657724257,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7536160469753668 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04270453599055899,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.416716206003912 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707354922619,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14708217481443256,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.798920408007689 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020409331415050296,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.997195432995795 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13751024276497106,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.272185547000845 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017450946359185787,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.30348253999546 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13791778672793975,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.250696401999448 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017742728938024966,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.36111578399141 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13498372990462762,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.408300250011962 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017462362621408614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.26601959198888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3674933578338718,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7211376170016592 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04254295963964154,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.505651897998177 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707441349136,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13434470078670258,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.443538852996426 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.01860897139354553,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 53.73752148100175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1353618051912144,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.387608332996024 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017261486069063046,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.932439652009634 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1373150381422468,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.282523556990782 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017624742665797614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.73841706299572 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1326304732425192,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.539745396003127 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.01750155270118318,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.137787547981134 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3615781962465679,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7656534890120383 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04197330203703812,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.824668336019386 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707527722343,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14804019741186955,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.754922091990011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020581469165184742,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.58739636000246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13843638259637925,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.223534603006556 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017682823060035685,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.552056004002225 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13993488820432465,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.146180718991673 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01805847140338209,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.37567259500793 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13690780482973855,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.304185479006264 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017824655330951934,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.102066571998876 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3697622577193757,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7044404319894966 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04280070597953046,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.364100594000774 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707614502621,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14725519797293038,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.790931754978374 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02054389737340949,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.676255621016026 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13718965613135253,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.289179287996376 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017488333005690308,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.18097886600299 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1371009207448469,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.293897039984586 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017860373820769992,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.98986953101121 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13486100861202988,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.41504168100073 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.01767979259614613,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.56174949801061 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36351463435007814,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7509208859992214 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04266628499208253,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.437709661986446 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707701407282,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1469089418848253,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.806937598012155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020604603424612063,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.532843820983544 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13735600872756043,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.280351324006915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01753500886631397,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.028770708013326 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13892526724207518,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.198114639992127 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017844881527838582,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.0384779489832 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1365335389477923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.324207719997503 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017627382404229373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.72992036299547 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3676932439348276,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.719658346992219 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04249066684376193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.53458004500135 sec\nrounds: 1"
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
          "id": "61be7abdfa931d79cc2c1f5ea05a80c3e279bd66",
          "message": "Merge pull request #450 from OpenTrafficCam/feature/2904-load-input-files-via-cli-option-when-starting-the-gui\n\nFeature/2904 load input files via cli option when starting the gui",
          "timestamp": "2024-02-06T11:30:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/61be7abdfa931d79cc2c1f5ea05a80c3e279bd66"
        },
        "date": 1707787004222,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1462853046363313,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.835956642986275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020372195841730042,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.08651024999563 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13599904264348767,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.352992937027011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01757427184483025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.90136176504893 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1386028801517379,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.214857287995983 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017782765182691427,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.23422396497335 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13549100122475502,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.380563955986872 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017483084782028348,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.198143946996424 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3599015094082595,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.778537944017444 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04250624796538344,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.525953191972803 sec\nrounds: 1"
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
          "id": "b53a8e2c30e4cf341743d600c0091365f063794e",
          "message": "Merge pull request #457 from OpenTrafficCam/task/4299-thicker-lines-for-bounding-boxes\n\ntask/4299-thicker-lines-for-bounding-boxes",
          "timestamp": "2024-02-13T08:09:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b53a8e2c30e4cf341743d600c0091365f063794e"
        },
        "date": 1707873412223,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1438790844642842,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.950280533987097 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.019995674749984368,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 50.01081546401838 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1370223155826591,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.29808130703168 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.01749768710113376,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 57.15041046397528 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13760507728411428,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.267173709988128 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.017762668348719493,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.29784784402 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1329090709912877,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.5239409360219724 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.0176479409195196,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.6638343000086 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3639364876309502,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7477321840124205 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04222974809465883,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.67998970201006 sec\nrounds: 1"
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
          "id": "b53a8e2c30e4cf341743d600c0091365f063794e",
          "message": "Merge pull request #457 from OpenTrafficCam/task/4299-thicker-lines-for-bounding-boxes\n\ntask/4299-thicker-lines-for-bounding-boxes",
          "timestamp": "2024-02-13T08:09:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b53a8e2c30e4cf341743d600c0091365f063794e"
        },
        "date": 1707959786366,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1470053409110812,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.802473935997114 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.020286987208162896,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 49.29268154699821 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13838370294096808,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.226284444972407 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017622092215834193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.746950801985804 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13879575861102605,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.204831113049295 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01788793327971652,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 55.903607440995984 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13622936562941293,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.340561232005712 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017748309399241456,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.34339460200863 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36805897310120583,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7169559040339664 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04251296956181942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.522233575000428 sec\nrounds: 1"
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
          "id": "b53a8e2c30e4cf341743d600c0091365f063794e",
          "message": "Merge pull request #457 from OpenTrafficCam/task/4299-thicker-lines-for-bounding-boxes\n\ntask/4299-thicker-lines-for-bounding-boxes",
          "timestamp": "2024-02-13T08:09:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b53a8e2c30e4cf341743d600c0091365f063794e"
        },
        "date": 1708047272770,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14788164043594765,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.762164640938863 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_2hours",
            "value": 0.02049911377136764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 48.78259670897387 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.138829432447522,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.20308354194276 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_2hours",
            "value": 0.017651202424820153,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.65336422598921 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13891983131434943,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.19839630194474 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_2hours",
            "value": 0.01781231050639106,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.14094811794348 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13430429030062865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.445778521010652 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_2hours",
            "value": 0.017607399658553735,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 56.794303496950306 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3665711490469661,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.727983374032192 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_2hours",
            "value": 0.04239364840551443,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.588439250015654 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708132187646,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14715502543290274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.795554532087408 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.12368199654685404,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.085251111071557 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13712373476008524,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.292683514999226 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1350189682617119,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.40636677108705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36125496994594974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7681280070682988 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06407926268898642,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.605672694044188 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007902544346478968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 126.54152335703839 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708218867528,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14617676671462437,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.841032419004478 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.12645034246710968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.908242717967369 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13858228881623952,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.215929312049411 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13706752044861523,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.295674399938434 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36458835301669595,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.742819378967397 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06493652003195942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.399654916953295 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007872439438013393,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 127.02542939502746 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708305104283,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14714913540330393,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.795826541958377 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13853998580495724,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.218132687034085 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13869904268550778,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2098550980445 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13788229615441847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.252562713925727 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3631417335577498,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.753745735040866 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06425883961511096,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.562061281991191 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007773509610400475,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 128.64202273089904 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708391377434,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14619300280210593,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.840272658970207 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1381454315630114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.238748242962174 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13633269672467793,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.334997575962916 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13679537757989288,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.310188528965227 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36611696557808115,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.731367551954463 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06357654587505723,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.729070937028155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007819684059695945,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 127.88240450201556 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708478739878,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14741448610233948,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.783593841013499 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1382857668292599,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.231402211007662 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1380960319645311,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.241337682004087 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13753895951287634,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.270667187985964 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.364985600872949,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7398341129301116 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06530134855679041,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.31361942901276 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007908726369400895,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 126.44260950398166 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708564190399,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1475146278696738,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.778988731093705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13822251151878154,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.234711545985192 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13702787365711488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2977852849289775 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13509051795193192,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.40244404389523 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3595036860161371,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.78161264793016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06364473969005455,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.71221761405468 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007872498967356648,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 127.02446886897087 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708650558684,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14764106251714088,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.773183441997389 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13559124410797174,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.375107490006485 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13573573818918996,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.367256504003308 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13356471216793106,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.487007486997754 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36102967633328564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.769855404010741 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06362663335299205,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.716688865999458 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007878161046677642,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 126.9331756580068 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708736860347,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14217829995093664,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.033422120992327 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13531901877855093,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.389944214985007 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13543311336943165,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.383718612982193 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1340837418260942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.458025756001007 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.35872569082148403,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.787645339005394 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06197439164410985,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.1356969140179 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007753531692642205,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 128.97348455400788 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708823676361,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14693642309004334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.805664511019131 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1363603086451025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.333512295008404 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13797847151900383,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.2475074480171315 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13617906769240087,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.343272478989093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3628242059285299,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7561556909931824 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06451808964542284,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.499528977001319 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007889564346324417,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 126.74971089701285 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708910018468,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14759943768225725,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.775093562027905 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.12737792889593152,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.850653631030582 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1369363124504932,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.302664881979581 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1342607778761494,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.448191614996176 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36109530785500493,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.769351964001544 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06424855924613095,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.564551357005257 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007869236768038924,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 127.07712697901297 sec\nrounds: 1"
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
          "id": "54e6bcba1e88a7ef6265b722fc76ea4e55b69a22",
          "message": "Merge pull request #464 from OpenTrafficCam/feature/4303-extend-benchmark-with-end-to-end-test\n\nFeature/4303 extend benchmark with end to end test",
          "timestamp": "2024-02-16T08:05:23Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/54e6bcba1e88a7ef6265b722fc76ea4e55b69a22"
        },
        "date": 1708996371761,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1420350709953618,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.040514662978239 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13569739623295843,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.369338157994207 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13542705587740295,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.384048877982423 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13356130056936327,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.487198729999363 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3533419728130074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.830119478981942 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06345783860871454,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.758494489011355 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007691763405139944,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 130.009199104039 sec\nrounds: 1"
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
          "id": "0ee04c95d5771cf391fa4193d70651738fa05f0a",
          "message": "Merge pull request #469 from OpenTrafficCam/bug/4360-use-all-detections-in-pythondetectionparser-to-determine-the-track-classification\n\nbug/4360-use-all-detections-in-pythondetectionparser-to-determine-the-track-classification",
          "timestamp": "2024-02-27T14:37:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/0ee04c95d5771cf391fa4193d70651738fa05f0a"
        },
        "date": 1709082574295,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14181064568626967,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.051656772033311 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1346369736567886,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.427380256995093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1296230090411361,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.714679726981558 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12665864857939318,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.895236616022885 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.35765858830922176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.795962497999426 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.061830800626783096,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.173169195011724 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00751584523513172,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.0522341420292 sec\nrounds: 1"
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
          "id": "0ee04c95d5771cf391fa4193d70651738fa05f0a",
          "message": "Merge pull request #469 from OpenTrafficCam/bug/4360-use-all-detections-in-pythondetectionparser-to-determine-the-track-classification\n\nbug/4360-use-all-detections-in-pythondetectionparser-to-determine-the-track-classification",
          "timestamp": "2024-02-27T14:37:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/0ee04c95d5771cf391fa4193d70651738fa05f0a"
        },
        "date": 1709168977935,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1464907693595139,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.8263686809223145 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13522456873685487,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.3951058549573645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12965178225985918,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.712967631989159 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12860930881151225,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.775486932019703 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36089470951829805,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7708912700181827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06186458428475133,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.16433718195185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007646619557191836,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 130.7767429150408 sec\nrounds: 1"
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
          "id": "6fa4830a9c64a62d391e2f0051d0d1b2cf2332e7",
          "message": "Merge pull request #471 from OpenTrafficCam/feature/4466-show-events-of-current-filter-range\n\nfeature/4466-show-events-of-current-filter-range",
          "timestamp": "2024-02-29T15:57:30Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6fa4830a9c64a62d391e2f0051d0d1b2cf2332e7"
        },
        "date": 1709255773567,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14661056124257604,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.820791022997582 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13842978046564894,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.223879115001182 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13310009970364878,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.513142381008947 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13006238543641516,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.68861801699677 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36753014478126983,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7208652520057512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06427044783155622,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.55925053799001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007830764348618499,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 127.7014548619918 sec\nrounds: 1"
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
          "id": "60950f41ae45d0e080e2648d10a118a66681980a",
          "message": "Merge pull request #470 from OpenTrafficCam/bug/4365-wrong-output-in-start_guicmd\n\nbug/4365-wrong-output-in-start_guicmd",
          "timestamp": "2024-03-01T07:46:59Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/60950f41ae45d0e080e2648d10a118a66681980a"
        },
        "date": 1709341722224,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14680569225992593,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.81172497200896 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13223561089914646,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.562259464000817 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13283027384489898,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.528404263983248 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13063927503205733,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.654665870999452 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3648051967000102,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7411890210059937 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06279075423181027,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.925911580998218 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007623375335112293,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 131.17549065098865 sec\nrounds: 1"
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
          "id": "60950f41ae45d0e080e2648d10a118a66681980a",
          "message": "Merge pull request #470 from OpenTrafficCam/bug/4365-wrong-output-in-start_guicmd\n\nbug/4365-wrong-output-in-start_guicmd",
          "timestamp": "2024-03-01T07:46:59Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/60950f41ae45d0e080e2648d10a118a66681980a"
        },
        "date": 1709428417642,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1463443659658767,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.8331978030037135 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13450979641969885,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.4344027469924185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1285049838600451,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.781799350981601 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1289715722800039,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.753646655008197 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.358688703870953,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7879327929986175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06273869784568133,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.939125839999178 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0076800858608920336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 130.20687764600734 sec\nrounds: 1"
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
          "id": "60950f41ae45d0e080e2648d10a118a66681980a",
          "message": "Merge pull request #470 from OpenTrafficCam/bug/4365-wrong-output-in-start_guicmd\n\nbug/4365-wrong-output-in-start_guicmd",
          "timestamp": "2024-03-01T07:46:59Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/60950f41ae45d0e080e2648d10a118a66681980a"
        },
        "date": 1709514666810,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14419324078348805,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.935137837019283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13130621009914864,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.615786025999114 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12826847062938693,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.796148149995133 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12613198773108214,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.928202972048894 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3509723827276071,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8492270309943706 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06175982465555091,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.19175581500167 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007458739784190572,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 134.07090593501925 sec\nrounds: 1"
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
          "id": "b8ec78cfbedf754326ad3d6d35654dc57c3251cb",
          "message": "Merge pull request #456 from OpenTrafficCam/feature/4235-keep-sections-selected-when-selecting-a-flow-and-vice-versa\n\nfeature/4235-keep-sections-selected-when-selecting-a-flow-and-vice-versa",
          "timestamp": "2024-03-04T09:03:09Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b8ec78cfbedf754326ad3d6d35654dc57c3251cb"
        },
        "date": 1709601003680,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13993799519656797,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.146022054948844 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.1357320799071182,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.367455067986157 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1303154853931098,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.673685111047234 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12734204233866972,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.852866041997913 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.35394842808152904,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.825270352012012 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0609282668396736,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.41274324496044 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007467929051852082,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.90593202703167 sec\nrounds: 1"
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
          "id": "22885ce42c80176de4cc873649783d0275640b1b",
          "message": "Merge pull request #474 from OpenTrafficCam/feature/extend-run-configurations\n\nAdd run configurations for scalene, cli and prefilled gui using test and benchmark data",
          "timestamp": "2024-03-05T11:46:00Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/22885ce42c80176de4cc873649783d0275640b1b"
        },
        "date": 1709640751881,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14238677418175996,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.02312420340022 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.2222895062130606,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.4986379115958695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.22178827861994185,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.508804550999775 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.17214112723259212,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 5.809187008801382 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.17094364551447672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 5.849881093797739 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.49332555807954687,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.0270589747931806 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.48962862866223017,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.0423642357927747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.7125090346370065,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1.4034909753943794 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.7051546226566926,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1.4181286881910637 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.05674504448511508,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.622684219805524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.06725497530459357,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.868788449792191 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.005157148152954636,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 193.90561805502512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.007158549652400944,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 139.6931010549888 sec\nrounds: 1"
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
          "id": "22885ce42c80176de4cc873649783d0275640b1b",
          "message": "Merge pull request #474 from OpenTrafficCam/feature/extend-run-configurations\n\nAdd run configurations for scalene, cli and prefilled gui using test and benchmark data",
          "timestamp": "2024-03-05T11:46:00Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/22885ce42c80176de4cc873649783d0275640b1b"
        },
        "date": 1709688135874,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14306657173312248,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.989753007190302 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.22356365619518337,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.4729989525978455 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.22503799104207436,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 4.443694130796939 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.17396559530788167,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 5.748263029998634 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.1739604268982012,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 5.748433812393341 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.5060962880029857,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1.9759085844038053 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.49859366680268286,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.005641199601814 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.7262347179354489,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1.3769652913906612 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.7108049269265845,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1.4068557520047762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.05805408421110975,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 17.22531693659257 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0696324213331326,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.361126338201576 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.005255778918257583,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 190.2667550429469 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0072160035016920155,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 138.58086401503533 sec\nrounds: 1"
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
          "id": "370a1e4797e36b62eb5a4e0dc00adef3b9a20c06",
          "message": "Fix bug where UI datetime and classification filter do not work when using tracks not assigned to flow highlighter",
          "timestamp": "2024-03-06T09:55:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/370a1e4797e36b62eb5a4e0dc00adef3b9a20c06"
        },
        "date": 1709719836785,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.145069443247121,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.893250415916555 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13504049310106103,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.405186229967512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13641250943205374,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.3307059899671 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1298324060020708,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.702237298013642 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.128712573333775,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.769248754018918 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1280031229647578,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.81230939400848 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12772876511745923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.829090018058196 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36219022919198984,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7609800579957664 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.36606580783524345,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.731749260914512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0630088607732868,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.870783691806718 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07320770667408036,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.659764052601531 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007510797727206288,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.1416497048922 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.009008818447016191,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 111.00234796397854 sec\nrounds: 1"
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
          "id": "0b024e84eacd23fcb68cb925ccad4c225ab5690f",
          "message": "Use loc",
          "timestamp": "2024-03-06T12:58:55Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/0b024e84eacd23fcb68cb925ccad4c225ab5690f"
        },
        "date": 1709730870740,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1459372731357287,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.852259046048857 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13644751741403519,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.32882516994141 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.1372945698255692,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.283609259058721 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13131432215955025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.615315553965047 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.13032694797924413,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.673010190948844 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12938238179870512,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.729027600958943 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.1300481202648479,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.6894613929325715 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.355641711261193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8118186600040644 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.36027565286793684,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.775652454001829 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06321675366768531,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.818591464799828 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07353606641545482,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.598769267182798 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00746037412221041,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 134.04153513198253 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.009077105816744811,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 110.16727359895594 sec\nrounds: 1"
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
          "id": "b918a1cfc0e64aec5dc798b3a6563071eb88b88f",
          "message": "Merge pull request #475 from OpenTrafficCam/revert-classification-as-multiindex\n\nPerformance drop due to internal datastructure changes of PandasTrackDataset",
          "timestamp": "2024-03-06T13:29:35Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b918a1cfc0e64aec5dc798b3a6563071eb88b88f"
        },
        "date": 1709773663477,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.144007234333976,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.944095583981834 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13278559831647044,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.530937185045332 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13615836784462865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.344388860045001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.1286338915674606,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.774000986944884 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.12761982520337345,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.835773152066395 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1262920423898913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.918155262013897 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12791711841796033,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.81756196799688 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.35746794551276095,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.797453625011258 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.36239256185143764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.759438535082154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.061349219117750126,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.30012597357854 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07170967264361122,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.945120136998593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007262085447198493,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 137.70149184705224 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00867022630508058,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 115.33724320598412 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1709860668834,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14416568807638452,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.936463269055821 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13425952630926774,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.448261047014967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13498396841122137,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.408287160098553 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12964112520473145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.713601670926437 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.12987010786019615,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.7000013049691916 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13012810100679179,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.684735212940723 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.1256083492620847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.961254214984365 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3596068677238986,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7808145220624283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3653064262580339,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7374278909992427 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0616772716902384,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.21342793861404 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07301281340226672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.696226092404686 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0074204425675288175,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 134.76285152800847 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.009019397055198254,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 110.8721562960418 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1709946931818,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14408842611049197,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.940182684993488 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.133703720342285,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.4792234459891915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13290655518009006,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.524083358002827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12759853079352806,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.837080832992797 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.12734633996578698,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.852601026999764 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.1280540502992083,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.809202424003161 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12725128128097085,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.858467042009579 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.356527442136847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.804833182002767 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3602113564345863,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7761478979955427 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06295223821680497,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.88505871000234 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07408928529145184,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.49722832480038 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007535920509901262,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.697790360995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.009046957993304723,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 110.53439186299511 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1710033727819,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14220804805629594,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.031950819015037 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13669800436111404,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.3153957489994355 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13657423070489957,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.322025500994641 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13160144628034934,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.598700685019139 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.1315877873492529,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.599489437008742 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13050919516158424,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.662295355985407 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12865326053211626,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.7728305980272125 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36296181454541593,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.755110758007504 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.36642128384879097,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7290991109912284 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0635660859085233,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.731659196998226 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07399213336265359,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.514950232597766 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007547259233128265,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.4984301069926 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00903816815384531,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 110.6418892609945 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1710119935854,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1472260018805061,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.792278451001039 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13715564464459307,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.290986839012476 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13763249341172096,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.265726102981716 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13068624425029216,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.651914749993011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.13223737000502794,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.562158865999663 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.13079154942236176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.645753907010658 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.13006282082742904,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.688592279009754 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.36541191821852986,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7366376139980275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3656394139918944,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7349349160213023 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0636841789854902,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.702487115800613 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0743594454086158,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.448190670396434 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0075899703266655485,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 131.75282075698487 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00887631815598534,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 112.65932365501067 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1710206547933,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14685666054245888,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.809360885003116 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13429769483634338,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.446144188987091 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13650342446990968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.325823538005352 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.13006268913366098,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.6886000640224665 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.13119418036785732,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.622289321036078 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12894395518094087,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.75530732399784 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12816280797471077,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.802575613022782 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3586054664249687,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7885799119831063 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.35782622523632907,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.794652625976596 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06333389220562285,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 15.789334354398306 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07399922997894343,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.513654132408556 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0075266021837527885,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 132.86207714799093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.009099713962305793,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 109.89356414304348 sec\nrounds: 1"
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
          "id": "8bedc90d44e9510ece4a57c50db2b52e71afa449",
          "message": "Merge pull request #476 from OpenTrafficCam/task/4441-clean-up-otanalytics-gui\n\ntask/4441-clean-up-otanalytics-gui",
          "timestamp": "2024-03-07T14:08:06Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8bedc90d44e9510ece4a57c50db2b52e71afa449"
        },
        "date": 1710292774748,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1419623025872936,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.04412355797831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13325309975900315,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.504515855980571 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13235091803843405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.555671051028185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12642130658373013,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.910059047979303 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.12658506323986213,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.89982620702358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12677034633397763,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.888280097977258 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.1248915133621528,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.00694917596411 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.35190753181328005,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.84165557596134 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3504381580368388,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.853570528968703 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06140055734742694,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.286497113399673 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07131268320319767,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 14.022751004202291 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007357117651117269,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.92279577697627 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.008731757925129018,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 114.52447589300573 sec\nrounds: 1"
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
          "id": "4013ce5b89f88e96b30c8837c1aeaa8d84b222fc",
          "message": "Merge pull request #478 from OpenTrafficCam/task/4602-export-tracks-as-csv\n\ntask/4602-export-tracks-as-csv",
          "timestamp": "2024-03-13T08:43:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/4013ce5b89f88e96b30c8837c1aeaa8d84b222fc"
        },
        "date": 1710379092775,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14366139904060118,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.960812066972721 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13273852295006267,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.533608012017794 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.1339951326497068,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.462957647978328 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12702636632330563,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8723813720280305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.1285602945281142,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.778451377002057 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12497226348428926,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.001775530981831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12707530331268757,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8693496999912895 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3555153884469687,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.81281776400283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.36100181309781776,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.7700691900099628 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06197603208023266,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.13526982020121 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07206838625535594,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.875709613598882 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007374201158256906,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 135.60790905199246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00881541958315898,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 113.43759540503379 sec\nrounds: 1"
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
          "id": "4013ce5b89f88e96b30c8837c1aeaa8d84b222fc",
          "message": "Merge pull request #478 from OpenTrafficCam/task/4602-export-tracks-as-csv\n\ntask/4602-export-tracks-as-csv",
          "timestamp": "2024-03-13T08:43:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/4013ce5b89f88e96b30c8837c1aeaa8d84b222fc"
        },
        "date": 1710465815912,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.14544416114323228,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 6.875490856007673 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.13207454969457913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.5714814270613715 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.13609632217874784,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.347737131989561 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.12893868138976766,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.755624528042972 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.12769614996412532,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.831089663086459 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.12485173110871388,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.009500478045084 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.12912339370546258,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.744530029012822 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3545357992787089,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8205896330764517 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3567731910604459,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8029011850012466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.06165256458036935,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.219925428996795 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.07310131139287791,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.67964515199419 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.007462734864365995,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 133.9991327810567 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.008988356918831188,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 111.25503905001096 sec\nrounds: 1"
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
          "id": "4013ce5b89f88e96b30c8837c1aeaa8d84b222fc",
          "message": "Merge pull request #478 from OpenTrafficCam/task/4602-export-tracks-as-csv\n\ntask/4602-export-tracks-as-csv",
          "timestamp": "2024-03-13T08:43:37Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/4013ce5b89f88e96b30c8837c1aeaa8d84b222fc"
        },
        "date": 1710552130467,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12815715328120153,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.802919887006283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08854700005880521,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.293437376036309 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08906043785619787,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.228330155019648 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08045611991013073,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.429135299054906 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0800767830524847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.48801415192429 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07999134951799282,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.50135178398341 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08436725489234803,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.852939879056066 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3329241231911831,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.003687418065965 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3294301638213431,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.0355447370093316 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.038658682264532264,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 25.867410408798605 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044703079073831586,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.369823750806972 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004649697456471574,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.06775642104913 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005694717523004358,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.60133509000298 sec\nrounds: 1"
          }
        ]
      }
    ]
  }
}