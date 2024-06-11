window.BENCHMARK_DATA = {
  "lastUpdate": 1718069901182,
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
        "date": 1710638855251,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12531228915661585,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.9800633020931855 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08742587115491458,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.4382617729716 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08879966058207242,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.261304305051453 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07906704248034924,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.64749469095841 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07973412200271883,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.541681966045871 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08124415019303986,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.308578496100381 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08072728005479225,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.387386262998916 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.32516095742028445,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.075399974011816 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3235339860689465,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.0908653899095953 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037827184748938536,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.4360143805854 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.045203273918024645,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.122291447594762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004650733805540447,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.01983166800346 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005619148938555066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.96289276808966 sec\nrounds: 1"
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
        "date": 1710725232192,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12656882705002082,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.90083959302865 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08753599176668729,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.423872396000661 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08762294814353565,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.412535428069532 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07864759814971438,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.714946464053355 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0795562959029075,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.56971542793326 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07704441028335932,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.979526954935864 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08074720918954129,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.38432894507423 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3242907444931054,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.0836526079801843 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.32806141310372744,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.048209756030701 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03869776780091245,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 25.84128379561007 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044759835021836274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.34145857580006 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00462480351323781,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.2254022549605 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005615610673436589,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.0750230300473 sec\nrounds: 1"
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
        "date": 1710811937419,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12864492792269075,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.773334061028436 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08727415833021779,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.45814544800669 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08836350218873482,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.31688961200416 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07989686620351108,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.51613545708824 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07876634490886016,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.6957776339259 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08049504452400254,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.42312499997206 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0813995314744677,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.285082996007986 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3218105251654653,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.107418564031832 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3235389885163583,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.0908176000230014 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03824229054777954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.149061305588113 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04512196746581957,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.162154182605445 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004665572320188674,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 214.3359766759677 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005673499661186782,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.258052299032 sec\nrounds: 1"
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
          "id": "588675817721fa8d0d77b89bd4d92a018fa23b04",
          "message": "Merge pull request #484 from OpenTrafficCam/feature/4643-move-time-filter-to-previous-or-next-event\n\nfeature/4643-move-time-filter-to-previous-or-next-event",
          "timestamp": "2024-03-19T14:51:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/588675817721fa8d0d77b89bd4d92a018fa23b04"
        },
        "date": 1710898423580,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12768340063519426,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.831871606060304 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09202761705489448,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.866303312010132 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09070913106597535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.024248476955108 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0822470444110151,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.158491617068648 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08401699551953683,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.902353729936294 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08305939961995222,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.03957655094564 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0814341703206071,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.279857411980629 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31711460496470495,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1534340719226748 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.32194380261240696,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.106132163084112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037216764841815034,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.86961116180755 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04604354968287201,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.718568765604868 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004692271666091131,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 213.11639034596737 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00572615965019967,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.63711476593744 sec\nrounds: 1"
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
          "id": "588675817721fa8d0d77b89bd4d92a018fa23b04",
          "message": "Merge pull request #484 from OpenTrafficCam/feature/4643-move-time-filter-to-previous-or-next-event\n\nfeature/4643-move-time-filter-to-previous-or-next-event",
          "timestamp": "2024-03-19T14:51:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/588675817721fa8d0d77b89bd4d92a018fa23b04"
        },
        "date": 1710984298794,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1318963901501474,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.581708634039387 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09086949484020931,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.004793212050572 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09173056455649548,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.901491829194129 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08173510144508585,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.234645609045401 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0806491121992381,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.399392538005486 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0779690435658049,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.825603011995554 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07780696624991902,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.852319634053856 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30665008980148833,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.261045841034502 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3075114626545564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2519112990703434 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03781076030253147,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.447497802181168 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.045302989040513976,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.073598700203 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004725275000774579,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 211.62789463810623 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0057629809499225165,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 173.52130931708962 sec\nrounds: 1"
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
          "id": "1d7e09d072628314b399f48c4ee2fd9d791264b3",
          "message": "Merge pull request #485 from OpenTrafficCam/task/4190-implement-regression-test-for-otanalytics-cli-using-test-data\n\ntask/4190-implement-regression-test-for-otanalytics-cli-using-test-data",
          "timestamp": "2024-03-21T09:01:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/1d7e09d072628314b399f48c4ee2fd9d791264b3"
        },
        "date": 1711070615122,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12470282762895898,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.019064354943112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0889259911754963,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.245306201046333 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09212556678295722,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.854750043014064 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08084556711006007,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.36926198611036 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08073677134455247,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.38593002106063 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0808052943794208,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.375426730141044 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08033316675799856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.448158591985703 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3154285122493884,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.170290449867025 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.32112324356960564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.114069193135947 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036959033372542686,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.056984686804935 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04557504185421022,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.941833936190232 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004718271044328753,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 211.94204203295521 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005714297574593081,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.9996367788408 sec\nrounds: 1"
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
          "id": "1d7e09d072628314b399f48c4ee2fd9d791264b3",
          "message": "Merge pull request #485 from OpenTrafficCam/task/4190-implement-regression-test-for-otanalytics-cli-using-test-data\n\ntask/4190-implement-regression-test-for-otanalytics-cli-using-test-data",
          "timestamp": "2024-03-21T09:01:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/1d7e09d072628314b399f48c4ee2fd9d791264b3"
        },
        "date": 1711156942811,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12786368000140239,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.820829182994203 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0871848826154698,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.469878378004069 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08801905120882188,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.361176771009923 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07934026425539702,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.603940879009315 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07860307481946238,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.722148622007808 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07979767603105659,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.53169327400974 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07982092074259055,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.528043910002452 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31538778428102854,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1706998490117257 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31911587389910023,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1336579649941996 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03808793063975931,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.255036259599727 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04439095634090937,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.527110979999996 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004632398014592996,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.87091542000417 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005659221377774778,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.70275347899587 sec\nrounds: 1"
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
          "id": "1d7e09d072628314b399f48c4ee2fd9d791264b3",
          "message": "Merge pull request #485 from OpenTrafficCam/task/4190-implement-regression-test-for-otanalytics-cli-using-test-data\n\ntask/4190-implement-regression-test-for-otanalytics-cli-using-test-data",
          "timestamp": "2024-03-21T09:01:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/1d7e09d072628314b399f48c4ee2fd9d791264b3"
        },
        "date": 1711243806474,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12618664967892054,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.9247686070157215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08930366357244053,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.197748894017423 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08959332026384569,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.161546385992551 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08025018624722695,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.461030270002084 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08010436698640835,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.48371390500688 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07627554485570985,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.110361936996924 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07592192399819375,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.171425951004494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3044710333897502,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2843846879841294 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3100708558873575,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2250693059759215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03732260075473802,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.79341685139807 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043791661974489055,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.83539730879711 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004650435589020349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.03362015399034 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0056265048916570555,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.73022849101108 sec\nrounds: 1"
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
          "id": "1d7e09d072628314b399f48c4ee2fd9d791264b3",
          "message": "Merge pull request #485 from OpenTrafficCam/task/4190-implement-regression-test-for-otanalytics-cli-using-test-data\n\ntask/4190-implement-regression-test-for-otanalytics-cli-using-test-data",
          "timestamp": "2024-03-21T09:01:13Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/1d7e09d072628314b399f48c4ee2fd9d791264b3"
        },
        "date": 1711329936408,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12973701086820014,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.707900723995408 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09146439112532191,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.933216606994392 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09147561449139748,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.93187518400373 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07823227086133258,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.782448840996949 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07966555793314234,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.552475950011285 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07705376985523357,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.977950356988003 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07681998275125418,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.017446296988055 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3062818850788044,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2649661919858772 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3092003802212106,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.234148674993776 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.038200174825349195,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.177890665997985 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044609104318474174,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.41694863140001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004684007461511121,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 213.49240115800058 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005847173781134333,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 171.02279450398055 sec\nrounds: 1"
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
          "id": "bf3e668e21b5635df3533c66de1015c51b45595e",
          "message": "Merge pull request #488 from OpenTrafficCam/bug/4709-activation-of-filter-by-date-is-broken\n\nbug/4709-activation-of-filter-by-date-is-broken",
          "timestamp": "2024-03-25T10:30:45Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bf3e668e21b5635df3533c66de1015c51b45595e"
        },
        "date": 1711416236832,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12574820656003488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.9523996990174055 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08700411297390953,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.493709501984995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08908476933514915,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.225263391970657 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08147165445763221,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.274207595968619 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08084242538147773,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.369742684997618 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08053548284147515,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.416887125000358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08023749328099397,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.463001511001494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30720913380122505,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2551115509704687 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31144910453675423,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.210797480016481 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036749101355170836,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.21154975560494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044997355499796346,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.223528224998155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004606959541043971,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.06290039903251 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005578555717169512,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.25786721502664 sec\nrounds: 1"
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
          "id": "b10e40a76d40e8117c0627081d5641307bf02b55",
          "message": "Merge branch 'main' into bug/4735-event-file-is-bigger-after-updating-event-creation",
          "timestamp": "2024-03-26T15:17:29Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b10e40a76d40e8117c0627081d5641307bf02b55"
        },
        "date": 1711470717803,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12689418952322082,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.880581480974797 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08720855077289692,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.466765485005453 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08767202515118153,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.40614692401141 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.054436699412813844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 18.36996017000638 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.05940886496540642,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.832504721009172 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.05951795544054599,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.80165241897339 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.060133654432756846,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 16.629622952954378 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3391065199944672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.948925900971517 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.34550216393455924,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8943378779804334 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.027005400874875463,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 37.02962991119129 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04506660812350244,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.189377937198152 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0008293417871949887,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 1205.7754902019515 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0038024645920385273,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 262.98732724395813 sec\nrounds: 1"
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
          "id": "bf3e668e21b5635df3533c66de1015c51b45595e",
          "message": "Merge pull request #488 from OpenTrafficCam/bug/4709-activation-of-filter-by-date-is-broken\n\nbug/4709-activation-of-filter-by-date-is-broken",
          "timestamp": "2024-03-25T10:30:45Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bf3e668e21b5635df3533c66de1015c51b45595e"
        },
        "date": 1711502678227,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12829196826515546,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.794720227015205 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08743350144487066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.437263560015708 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08825647588451818,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.330613306025043 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07813029488994155,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.79913254402345 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07847488170706544,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.74293096398469 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0770641726200165,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.976198485004716 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0772375224266866,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.947075056028552 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29485359999758665,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3915136189898476 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3039329843655325,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2901989959646016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036552773386049786,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.357705239998175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044790927269368216,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.32594994039973 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004577691612625207,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.45071372698294 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005598743596631749,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.61150144500425 sec\nrounds: 1"
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
          "id": "bf3e668e21b5635df3533c66de1015c51b45595e",
          "message": "Merge pull request #488 from OpenTrafficCam/bug/4709-activation-of-filter-by-date-is-broken\n\nbug/4709-activation-of-filter-by-date-is-broken",
          "timestamp": "2024-03-25T10:30:45Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/bf3e668e21b5635df3533c66de1015c51b45595e"
        },
        "date": 1711531476557,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13874428720404425,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.207503963960335 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0983767347183875,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.16500499699032 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09994204115155597,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.005799246020615 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08665165031776523,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.54046110296622 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08647478401938712,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.56406473100651 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07793860869087388,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.83061138499761 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07780911596731961,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.85196454898687 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30595858490135774,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2684162149671465 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30911890456394375,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2350011119851843 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03892479312343372,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 25.690566853596827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04686474714064764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.338000544393434 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0048689352724187295,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 205.38371205399744 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005970767873478734,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 167.48264564794954 sec\nrounds: 1"
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
          "id": "7bb4c27ff5aa0375e484477ca502de1fef8c61d3",
          "message": "Speed up removing duplicate events",
          "timestamp": "2024-03-27T15:31:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/7bb4c27ff5aa0375e484477ca502de1fef8c61d3"
        },
        "date": 1711554710619,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12741835818348238,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8481626529828645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.087615963279099,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.413445251004305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08735985569055534,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.446905355958734 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07939759677042979,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.594839651021175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07914116852304194,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.63564866001252 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08733119110841164,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.450662556046154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08625585268194023,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.59341620199848 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3457524859071835,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8922424010233954 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.35145559726841435,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 2.8453096430166624 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.040726653429113184,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 24.553944795404096 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0458524312371672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.80909437119262 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004697430275070499,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 212.88235086895293 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005850513945921365,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 170.92515448102495 sec\nrounds: 1"
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
          "id": "affd88cc2a74e88d4a1e3d3c57ac99dec5a1b6cc",
          "message": "Merge pull request #490 from OpenTrafficCam/bug/4735-event-file-is-bigger-after-updating-event-creation\n\nbug/4735-event-file-is-bigger-after-updating-event-creation",
          "timestamp": "2024-03-27T17:07:30Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/affd88cc2a74e88d4a1e3d3c57ac99dec5a1b6cc"
        },
        "date": 1711589046909,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12933336969558923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.73195658903569 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08972542629073506,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.14511283300817 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0915577049174606,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.92207369004609 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08067720388129838,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.39507508801762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08029899416541739,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.453456116025336 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08157019187520889,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.259380259027239 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07810329421600777,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.803557263978291 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31274642864769275,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.197478558984585 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30719951477493634,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2552134749712422 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037076980830898325,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.970912344800308 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04539049264847222,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.031045305996667 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004643173194642091,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.369954572001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005693756106329069,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.63098617596552 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "KueblerJelle",
            "username": "KueblerJelle",
            "email": "jelle.kuebler@gmail.com"
          },
          "committer": {
            "name": "KueblerJelle",
            "username": "KueblerJelle",
            "email": "jelle.kuebler@gmail.com"
          },
          "id": "c940583effb42f6b8c77843dd8823f1c6ed42e3e",
          "message": "fixed MetadataFixer for recorded start date -> catch TypeError\n\nfixed test_cli patches",
          "timestamp": "2024-03-28T17:04:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c940583effb42f6b8c77843dd8823f1c6ed42e3e"
        },
        "date": 1711646837512,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13826765022483384,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.232349709956907 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09800916033216946,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.203127917950042 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.1008208023359257,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 9.918587998021394 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.09017324404536961,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.089764049043879 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08991107695734077,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.122100122040138 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08960026755298399,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.160680959001184 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08019174042068448,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.47011219302658 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3038004673173381,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.291634173016064 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30609051961269085,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.267007424030453 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03065216189687616,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 32.62412626438309 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.034984394173574795,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 28.5841737043811 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00389051534549369,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 257.0353568090359 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.004436452839235059,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 225.40530379500706 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1711675475415,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12572904865817752,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.9536114420043305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08866748586939788,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.278091288986616 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09021356289069388,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.084807737963274 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08118200883458247,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.318000186933205 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08001426327196058,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.49777176103089 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07981351756127358,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.529205961036496 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08010288905286611,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.483944235020317 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.28905499262639966,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.4595493089873344 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30436304997369934,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.285549938096665 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03652514304375458,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.37840064861812 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0448132070207203,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.314850163203666 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004572232652518821,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.71153023000807 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005593171391030425,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.78944342804607 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1711761729076,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12608492865974152,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.931162039982155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08537961909407742,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.71239706396591 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0888919149118344,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.249617032008246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07870997068803987,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.704870695015416 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07877245085423011,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.694793537026271 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07748167251802363,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.906277930014767 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08089701348070669,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.361395766958594 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31821738601636795,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1425058590248227 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3107342443142398,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.218184085912071 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03800741661698987,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.3106543145841 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04423749861007888,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.605256432201713 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004614441415410433,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.71095371595584 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0056769682484645095,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.15035988099407 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1711848673870,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13108692927627089,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.628525631967932 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08899961676916654,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.236003438010812 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08716359333939451,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.472679839003831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07863967637684366,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.716227305005305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07837067575179579,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.759874664945528 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07747957393253278,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.906627505086362 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07772774520212836,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.865418871981092 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3120894750666137,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.204209304996766 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3121527413920454,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2035598839865997 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03793574253485944,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.360364478989503 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04445245173213531,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.49594704080373 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00462147608327712,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.38108300906606 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0056488137109845776,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.02831977896858 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1711935027795,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13093488000328668,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.637384323985316 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08994253351409358,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.118210271932185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09001065642400011,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.109795658965595 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08083151195955145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.371412778971717 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07786110868436324,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.843382490915246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07785539211137689,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.844325523008592 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.077247478027926,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.945406446000561 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30200445913119917,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.311209387029521 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3056735916979302,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2714635060401633 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03778343875372522,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.466622228804045 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04442255726766234,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.511085842596366 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004633112024222584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.83764751895797 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005713032694739161,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.03838213998824 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1712021392309,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12909331812052266,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.746334315044805 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08765043986011488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.408955866005272 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08983282599337394,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.131788284983486 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08013539896308461,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.478879657923244 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08016546047752557,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.474200161057524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0783506168259372,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.763141383067705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0765160225309214,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.069158156984486 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3001237248093967,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3319591799518093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30280279252466463,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3024794509401545 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036872085055271606,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.120787948416545 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04451100737321985,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.46635290940758 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004553158565949848,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.62775631807745 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005663378175658488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.5730574550107 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1712107473509,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12673438179682245,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.890518625034019 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08749564602014688,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.429140139953233 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09024615783552181,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.080804147059098 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08011809086128775,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.48157549998723 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08038852783931628,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.439585931948386 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07905871281055261,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.64882723800838 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07846966773507329,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.74377767695114 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29659207065258053,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3716343049891293 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29880633404708284,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3466492709703743 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03628511570733242,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.559509746800178 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04463807068665042,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.40240190979093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004567040493344739,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.9601781410165 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005656286689852826,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.79443331505172 sec\nrounds: 1"
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
          "id": "97ce2eb8bc6d400137addecfc04f38e6eccacc6c",
          "message": "Merge pull request #493 from OpenTrafficCam/integrate-regression-test-in-ci-pipeline\n\nIntegrate regression test in ci pipeline",
          "timestamp": "2024-03-28T11:45:56Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/97ce2eb8bc6d400137addecfc04f38e6eccacc6c"
        },
        "date": 1712193944310,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13302100423609273,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.51760976202786 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08869202577376416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.27497079106979 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08932437468753161,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.19515253813006 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07735533125965627,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.927357219159603 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07778281129364684,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.856310839997604 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07588812452221791,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.177292314125225 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07629786089835114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.106527341995388 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2981538067898962,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3539736110251397 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30320803740712154,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2980656072031707 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.038002725834586144,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.313901912001892 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0442541375612385,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.596757164597513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004604748259676099,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.16713783401065 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005678852134744978,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.0919242608361 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Steven Schlechte",
            "username": "StevenSchlechte",
            "email": "96142435+StevenSchlechte@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "14f6f4fe9119e7ed2a84f3b49198dcc2934a114e",
          "message": "Merge pull request #494 from OpenTrafficCam/task/4790-integrate-regression-test-into-cicd\n\ntask/4790-integrate-regression-test-into-cicd",
          "timestamp": "2024-04-04T08:44:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/14f6f4fe9119e7ed2a84f3b49198dcc2934a114e"
        },
        "date": 1712280311080,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12681904564092483,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.885250949067995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08856425288719331,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.29123734915629 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08921312137032758,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.209113464923576 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07958429354450204,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.565293419873342 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07888821360039364,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.676164845936 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07661614399965418,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.052079467801377 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07642624813289728,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.084509895881638 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3010998843368531,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.321157037978992 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3014421963757904,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3173855950590223 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0370581296954455,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.984632204007358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044327111262618166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.559557153983043 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004610036954176865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.91800086200237 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005681887247024509,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.99786066217348 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Steven Schlechte",
            "username": "StevenSchlechte",
            "email": "96142435+StevenSchlechte@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "14f6f4fe9119e7ed2a84f3b49198dcc2934a114e",
          "message": "Merge pull request #494 from OpenTrafficCam/task/4790-integrate-regression-test-into-cicd\n\ntask/4790-integrate-regression-test-into-cicd",
          "timestamp": "2024-04-04T08:44:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/14f6f4fe9119e7ed2a84f3b49198dcc2934a114e"
        },
        "date": 1712366604249,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12734611530963044,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.852614880073816 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08658287706122605,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.549627754837275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08669771596923036,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.534329236019403 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07929020715149511,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.61189793702215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07994348509104376,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.508836697088555 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07889481764900771,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.675103762187064 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07851262591205292,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.736804920015857 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31463889841952264,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1782465709839016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.32159271483286245,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1095231759827584 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03687280890951224,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.120255537191404 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044268542991422584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.58940395200625 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004613359576322819,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.76177272899076 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005653663975013457,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.87644763104618 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Steven Schlechte",
            "username": "StevenSchlechte",
            "email": "96142435+StevenSchlechte@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "14f6f4fe9119e7ed2a84f3b49198dcc2934a114e",
          "message": "Merge pull request #494 from OpenTrafficCam/task/4790-integrate-regression-test-into-cicd\n\ntask/4790-integrate-regression-test-into-cicd",
          "timestamp": "2024-04-04T08:44:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/14f6f4fe9119e7ed2a84f3b49198dcc2934a114e"
        },
        "date": 1712453443876,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12811459989778268,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.805511634098366 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08927623861688436,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.201188754057512 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09011245187779723,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.09724548785016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08131036412127671,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.298555181827396 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07785980236528629,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.843597975093871 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07837392996649578,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.75934485392645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07661918555484284,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.051561338827014 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3038385047037539,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2912220950238407 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30370499914181825,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2926688820589334 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037476854296723545,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.683135998621584 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04374469614332592,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.859914187621325 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00461184514988699,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.83295243000612 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005628387018694409,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.67079567885958 sec\nrounds: 1"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "Steven Schlechte",
            "username": "StevenSchlechte",
            "email": "96142435+StevenSchlechte@users.noreply.github.com"
          },
          "committer": {
            "name": "GitHub",
            "username": "web-flow",
            "email": "noreply@github.com"
          },
          "id": "14f6f4fe9119e7ed2a84f3b49198dcc2934a114e",
          "message": "Merge pull request #494 from OpenTrafficCam/task/4790-integrate-regression-test-into-cicd\n\ntask/4790-integrate-regression-test-into-cicd",
          "timestamp": "2024-04-04T08:44:43Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/14f6f4fe9119e7ed2a84f3b49198dcc2934a114e"
        },
        "date": 1712539588181,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12953175086099464,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.720114901196212 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08612971020858294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.61039550206624 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08770038194327241,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.40245889290236 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07788406441678243,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.839597002137452 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07807888679858849,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.807559648994356 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07721364131694372,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.951079407008365 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07701492011260844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.984497010940686 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30314273370130873,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2987760840915143 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30359725175033403,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2938374581281096 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.038074938395840294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.2639952192083 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04380101838553685,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.830519400211053 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004608083862904402,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.00993943493813 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005653648054309422,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.8769457160961 sec\nrounds: 1"
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
          "id": "c8ec433c451e346fccfa36ae8a916607978af99c",
          "message": "Merge pull request #492 from OpenTrafficCam/feature/4555-use-otanalytics-parser-to-read-existing-otconfig-files\n\nfeature/4555-use-otanalytics-parser-to-read-existing-otconfig-files",
          "timestamp": "2024-04-08T11:07:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c8ec433c451e346fccfa36ae8a916607978af99c"
        },
        "date": 1712625957701,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1313651259965611,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.612370424903929 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08903340794837838,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.23173899599351 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08811137845292069,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.349271995946765 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08009699456393359,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.48486295202747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0776599464070274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.876650657970458 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07768243578302131,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.872922816080973 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07817131261919599,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.792416635900736 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30981366152662176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2277466238010675 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3091253781488381,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.234933365834877 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.038043171018669115,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.285926572978497 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044189669349352194,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.629723524162547 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004621717621878593,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.3697745760437 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00573545094808171,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.35420667915605 sec\nrounds: 1"
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
          "id": "c8ec433c451e346fccfa36ae8a916607978af99c",
          "message": "Merge pull request #492 from OpenTrafficCam/feature/4555-use-otanalytics-parser-to-read-existing-otconfig-files\n\nfeature/4555-use-otanalytics-parser-to-read-existing-otconfig-files",
          "timestamp": "2024-04-08T11:07:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c8ec433c451e346fccfa36ae8a916607978af99c"
        },
        "date": 1712712334287,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1301298986387478,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.684629054972902 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08931939272927039,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.195776968961582 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09072082382078349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.022827592212707 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07899563167963163,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.658927825978026 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07871883983678564,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.703439253848046 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07664171965251793,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.04772393591702 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07691872485645145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.000735540874302 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3022203660016392,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3088438520208 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30318077073369204,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2983622199390084 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03797154981044941,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.33550658300519 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0444515210716518,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.496418027812616 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0046854631703294475,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 213.4260720119346 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005733394956744485,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.41672997316346 sec\nrounds: 1"
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
          "id": "c8ec433c451e346fccfa36ae8a916607978af99c",
          "message": "Merge pull request #492 from OpenTrafficCam/feature/4555-use-otanalytics-parser-to-read-existing-otconfig-files\n\nfeature/4555-use-otanalytics-parser-to-read-existing-otconfig-files",
          "timestamp": "2024-04-08T11:07:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c8ec433c451e346fccfa36ae8a916607978af99c"
        },
        "date": 1712798776733,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1324392560816597,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.55063135799719 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09100983894971358,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.987822982002399 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08700396603078002,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.493728913992527 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07818228620114706,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.790621106003528 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07618125017385392,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.126589517996763 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07700162096942298,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.986739596002735 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07783372147166576,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.847901668996201 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2991047195448243,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.343310668991762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30889274931468796,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2373696120048407 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037954260633678016,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.34750310779782 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04321158907829039,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.141939959398588 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0045805789162890595,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.313016383996 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005663803844991392,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.5597869149933 sec\nrounds: 1"
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
          "id": "dee55c15d0a8a2d1f875bfb987c3ba022a64b519",
          "message": "Merge pull request #498 from OpenTrafficCam/feature/4856-export-metadata-for-trackscsv\n\nfeature/4856-export-metadata-for-trackscsv",
          "timestamp": "2024-04-11T13:20:00Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/dee55c15d0a8a2d1f875bfb987c3ba022a64b519"
        },
        "date": 1712885161153,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13172519587368517,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.591562065004837 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09044693360402895,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.056206773995655 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08747008832187454,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.432479595998302 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07897507177263842,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.662223377003102 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07806704151575868,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.809502968011657 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07891596606575178,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.671707004978089 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07930971783343202,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.60879533199477 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31255690117834584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1994174380088225 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3167974865050596,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.156590700993547 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03804595319788465,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.284004367003217 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04438390983147284,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.530687445000513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0046132018306062105,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.76918477000436 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005704833915366245,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.28994092298672 sec\nrounds: 1"
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
          "id": "a3e63c9d6b8687877bf176f7683246617bae820c",
          "message": "Merge pull request #501 from OpenTrafficCam/feature/4639-export-vehicle-flow-assignment\n\nFeature/4639 export vehicle flow assignment",
          "timestamp": "2024-04-15T07:15:48Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/a3e63c9d6b8687877bf176f7683246617bae820c"
        },
        "date": 1713230701302,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1297534808339294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.706922338984441 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0919260544846042,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.878308718965854 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09161959072349624,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.914696214022115 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08104301108497375,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.339126923005097 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08168545230340074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.242081935051829 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0767797619219242,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.024265444022603 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0768883614138039,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.005869570013601 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29494608590025223,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3904501459910534 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2974393720194542,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3620296909939498 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037366088175562036,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.762234122597146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04459627065214002,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.423399655998217 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004639950603578019,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.51953575300286 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005733544301351794,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.41218684997875 sec\nrounds: 1"
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
          "id": "b93761c8feacbe93d43a3e423aa5bcc043301c84",
          "message": "Merge pull request #499 from OpenTrafficCam/feature/4837-add-additional-metadata-to-otanalytics-otconfig\n\nfeature/4837-add-additional-metadata-to-otanalytics-otconfig",
          "timestamp": "2024-04-16T12:19:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b93761c8feacbe93d43a3e423aa5bcc043301c84"
        },
        "date": 1713317145547,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13268360799420603,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.536726013990119 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.09121994680202769,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.962514615035616 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09061563472978783,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.035623189993203 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07826840788374119,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.776547102956101 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07850025140273906,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.73881270608399 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07687337678308302,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.008404753985815 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07740339810141995,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.91932944196742 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3016005004227875,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3156443659681827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3029582408346389,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.300784943974577 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03801526790614471,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.305220378004016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04413890742167751,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.655748826009223 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0046150410808717115,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.6827949039871 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005730680878205012,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 174.4993345909752 sec\nrounds: 1"
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
          "id": "b93761c8feacbe93d43a3e423aa5bcc043301c84",
          "message": "Merge pull request #499 from OpenTrafficCam/feature/4837-add-additional-metadata-to-otanalytics-otconfig\n\nfeature/4837-add-additional-metadata-to-otanalytics-otconfig",
          "timestamp": "2024-04-16T12:19:25Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/b93761c8feacbe93d43a3e423aa5bcc043301c84"
        },
        "date": 1713403515275,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12989548060954006,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.698497247998603 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08928819689607416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.199688590015285 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09130216141422785,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.952643228927627 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08135304013156407,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.292103631072678 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0794526430696534,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.586113707046025 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0769340486534896,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.998146041994914 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07682014333232856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.017419085954316 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29548122993624343,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.384309724904597 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3003065069923743,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3299311760347337 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03727696134586602,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.826220912206917 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04429100068200856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.57795002600178 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004585352225568557,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.08575455204118 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005692038510700373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.6839835359715 sec\nrounds: 1"
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
          "id": "76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5",
          "message": "Merge pull request #504 from OpenTrafficCam/feature/4893-export-road-user-assignment-on-event-export\n\nfeature/4893-export-road-user-assignment-on-event-export",
          "timestamp": "2024-04-18T10:28:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5"
        },
        "date": 1713489955702,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13161639950732168,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.597837380017154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08470527789583752,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.805639800033532 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08982528431054387,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.132722903974354 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0773936075057662,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.9209637879394 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07740677868811274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.918765216018073 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07615110283826969,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.131786182057112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07630121114710672,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.105951857985929 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29411585468466794,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.400020719971508 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29510287412603625,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.388648799038492 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03775373183939302,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.487447764212266 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043721814585109466,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.87187779119704 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004593661152115005,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.69128520495724 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005677585615003179,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 176.13120572897606 sec\nrounds: 1"
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
          "id": "76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5",
          "message": "Merge pull request #504 from OpenTrafficCam/feature/4893-export-road-user-assignment-on-event-export\n\nfeature/4893-export-road-user-assignment-on-event-export",
          "timestamp": "2024-04-18T10:28:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5"
        },
        "date": 1713576401709,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12773612871296583,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.828638695064001 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08543152730779584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.705280609079637 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08685633048404764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.513265578076243 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07572293238938844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.206039022072218 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07651566807709018,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.069218699005432 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0748242252255274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.364655590965413 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.075757086556747,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.20008523890283 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29134627576709765,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.4323417979758233 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2957285484780686,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3814794180216268 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03719958574340557,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.882019786396995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.042937502410473255,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.28966390360147 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004496262128781405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.40696190705057 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005535156314552711,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.66337121697143 sec\nrounds: 1"
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
          "id": "76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5",
          "message": "Merge pull request #504 from OpenTrafficCam/feature/4893-export-road-user-assignment-on-event-export\n\nfeature/4893-export-road-user-assignment-on-event-export",
          "timestamp": "2024-04-18T10:28:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5"
        },
        "date": 1713663043251,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12726851743112866,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.857402759022079 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08898708381051983,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.237585918977857 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09064083772644127,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.032554697012529 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07813537945486991,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.798299656016752 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0791574852229458,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.633044078946114 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07742312283310654,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.916038044029847 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07780766855414188,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.852203627000563 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3044618420174266,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.284483839990571 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30293969550656935,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3009870110545307 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037742994917904664,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.49498276899103 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0443996966293332,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.52267641259823 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004617168680107423,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 216.58294710097834 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005616489679523041,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.04715348198079 sec\nrounds: 1"
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
          "id": "76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5",
          "message": "Merge pull request #504 from OpenTrafficCam/feature/4893-export-road-user-assignment-on-event-export\n\nfeature/4893-export-road-user-assignment-on-event-export",
          "timestamp": "2024-04-18T10:28:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5"
        },
        "date": 1713749293611,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11435707647340917,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.744539741994231 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0861490841664533,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.60778445500182 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08801913051863064,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.361166533999494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07811605158057515,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.801466276985593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0806746957889005,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.395460438012378 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07961680141758512,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.560162958005094 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07687105217971332,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.008798131995718 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3146950950560239,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1776790160074597 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31087825375100203,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2166933130065445 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03718068162272735,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.895687662399723 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044410541777925014,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.517176327199557 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004519969307293568,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.2404403690016 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005537264741089136,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.59457995199773 sec\nrounds: 1"
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
          "id": "76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5",
          "message": "Merge pull request #504 from OpenTrafficCam/feature/4893-export-road-user-assignment-on-event-export\n\nfeature/4893-export-road-user-assignment-on-event-export",
          "timestamp": "2024-04-18T10:28:03Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/76ae07cb2246d199986e0c5c7e6d3e6d36ef04a5"
        },
        "date": 1713835622174,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12441518787118803,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.037603906006552 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.087151296231798,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.474298641987843 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08704313860868003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.488556317985058 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07758869250045498,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.888475985004334 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07810290310219942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.803621380007826 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07713108810569168,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.964940915000625 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07553484070796385,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.23892379499739 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3084525238642138,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.241990006994456 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30416903326715855,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2876456530066207 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03764665220992662,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.562786895997125 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04340696921727235,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.037775224400683 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004523834853073294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.0513938899967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0055415811083079705,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.4539138659893 sec\nrounds: 1"
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
          "id": "4e04d52511d8afbc822757fef843374264efe4e4",
          "message": "Merge pull request #506 from OpenTrafficCam/bug/4915-moving-to-the-next-video-using-the-date-range-filter-or-the-video-control-does-not-work\n\nbug/4915-moving-to-the-next-video-using-the-date-range-filter-or-the-video-control-does-not-work",
          "timestamp": "2024-04-23T19:41:52Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/4e04d52511d8afbc822757fef843374264efe4e4"
        },
        "date": 1713922050649,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12749155340370968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.843656880024355 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08645128085559284,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.567208607011707 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08739852055214775,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.441841276973719 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07842126243685901,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.751643736992264 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07789813053747506,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.837278546998277 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07713848297404131,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.963698033010587 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07888460942419369,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.676744010008406 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3091954502421872,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.23420024200459 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31336848322035754,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1911313790187705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03725816771140217,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.839752500603208 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0442144294173049,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.617050885397475 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004495514075492036,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.44397041300545 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005583306247554398,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.10534648498287 sec\nrounds: 1"
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
          "id": "4e04d52511d8afbc822757fef843374264efe4e4",
          "message": "Merge pull request #506 from OpenTrafficCam/bug/4915-moving-to-the-next-video-using-the-date-range-filter-or-the-video-control-does-not-work\n\nbug/4915-moving-to-the-next-video-using-the-date-range-filter-or-the-video-control-does-not-work",
          "timestamp": "2024-04-23T19:41:52Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/4e04d52511d8afbc822757fef843374264efe4e4"
        },
        "date": 1714008519691,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12321378883231579,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.11597475799499 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08618507997999421,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.602936381008476 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08967236232880395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.151707995973993 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08080109724911821,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.376069559017196 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08032626267869622,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.449228516954463 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07870466600159778,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.705727002001368 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.078695282914125,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.707241946016438 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3003147777279373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3298394689918496 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30041873267425606,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.328687232977245 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03681396082294492,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.163607980392406 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04500067093223674,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.221890902600716 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004562393685946264,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.18318953498965 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005595027023335706,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.73014658002649 sec\nrounds: 1"
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
          "id": "8e63968854c84bb53d444eef138d39d09dfb7ea1",
          "message": "Merge pull request #508 from OpenTrafficCam/feature/4920-display-selected-road-user-track-on-image\n\nMake use cases GetCurrentVideoPath and GetCurrentFrame be dependent on VisualizationTimeProvider",
          "timestamp": "2024-04-25T07:32:09Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/8e63968854c84bb53d444eef138d39d09dfb7ea1"
        },
        "date": 1714094862046,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12627794341027065,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.919039327010978 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08745183503154663,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.43486582802143 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08899442140051367,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.23665938002523 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07963982351442882,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.55653209501179 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07826060427072125,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.777821092982776 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07901530526686112,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.655775949009694 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07916128874821504,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.632437089050654 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31177059777984373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2074865530012175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3149326719341966,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1752818590030074 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03730232319540942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.807981764606666 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04485095579422349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.29606888620183 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004596674679338628,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.54856929398375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005621531087538943,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.88748019497143 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714181284932,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12198349185188341,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.19783058197936 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08688044342072501,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.510070168005768 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08694138929577665,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.502001613960601 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0784265616975906,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.750782112008892 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08023577167889209,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.463268927007448 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07870522028884092,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.70563752099406 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07881798158581974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.687460143992212 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30612998724373464,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2665862269932404 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3103389086514799,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2222836780129 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03722972621926786,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.860256616189144 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04499496241507386,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.224710197001695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004586552954604645,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.02866115304641 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005573928575041917,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.4066763750161 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714267903201,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12668602185668099,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.893530678004026 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08722505227708764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.464596166973934 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08754572763649084,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.422601958969608 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07868946752203469,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.708181050023995 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07833103771491096,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.766331573948264 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07746888863767003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.908407718059607 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07777948644644181,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.856860409956425 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3033635006856004,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2963754629017785 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3154576472019085,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.169997649034485 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03866677221870179,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 25.861998367588967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04340770459482628,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.03738493740093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004558000518435244,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.3944463049993 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005624542812406473,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.7922283379594 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714354087380,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12373404623991045,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.081849987036549 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08542254978540133,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.706510780961253 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08635692099872423,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.57984778098762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07820840438766308,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.786349597969092 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07978111269882435,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.534294974990189 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08012984930544377,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.479743923991919 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07826179031702209,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.777627446921542 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30937871297373265,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2322844399604946 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3134478463013435,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1903234040364623 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03680841838324809,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.167698149592617 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043982345470170346,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.73639546299819 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004524671641735633,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.01051284605637 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005527218979398719,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.92281194706447 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714440400977,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1268005281273767,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8864024840295315 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08599122992425183,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.629092884017155 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08697748478096665,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.497228305903263 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07790460143137942,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.836212259950116 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0779272710562651,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.832478109980002 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0768547756169041,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.011553179007024 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07667971640754916,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.04125845595263 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.296090148158368,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.377349791000597 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3115080486618621,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.21018992702011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03828208707192067,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.12187778898515 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0438579036871281,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.800907383393497 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004576067485590321,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.52824573696125 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00562926842111363,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.64297688298393 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714527115527,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12362136980236244,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.089216302963905 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.07982219945423084,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.527843217016198 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08690578573397899,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.506713753915392 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07738436216540137,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.922507493989542 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07775878465200756,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.860283304005861 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07598635495670614,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.160257530049421 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07653215083208359,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.066403976990841 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30019522890706535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.331165533978492 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30849082242319403,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.241587519994937 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03809861374532042,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.247674172208644 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04288399423469019,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.318723403592593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004508201536341441,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.8179449030431 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005552129483857637,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.11107322108 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714613185026,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1318676527332554,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.58336088701617 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08631400706290943,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.58560509502422 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08747811373499166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.431430757977068 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07789030423312426,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.83856841805391 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07863197524401984,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.717472718912177 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07742306402885658,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.916047853999771 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07690099569488479,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.00373279908672 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2956156529393377,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.382770804106258 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30037164388797455,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3292090659961104 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03810156596964643,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.245640423195436 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04377185651459546,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.845729645178654 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004564269266681563,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.09312128007878 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005622496731258482,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 177.85692865599412 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714700733504,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1282058726372145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.799954709014855 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.089988393590781,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.112544185947627 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09207834538404938,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.860316785983741 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08199273657299437,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.196202271035872 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0773340931427608,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.930907435016707 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0775111139638402,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.90137567196507 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07670894114648222,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.036289968993515 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2987725948218355,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.34702719503548 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3025227045890266,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.30553702195175 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03747003813204913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.687989920796827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04403139277622201,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.71106901119929 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004585355623308032,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.0855929509271 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005702829995275413,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.35153613705188 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714785999373,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12783875418700416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.822354076895863 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08499630698950177,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.765217047883198 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0874846134421744,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.430581454886124 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07758068950609343,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.889805522048846 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0772055521372233,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.952436350984499 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07573955784993977,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.203140187077224 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07597063542725437,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.162980596069247 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29703866234686965,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.366565120173618 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2950387007968728,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.389385857852176 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037580439972734865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.609587347181513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.042939203625138034,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.28874118695967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0045029302241956235,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.07761395606212 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005564483372385019,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.7112028338015 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714873354455,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12587650921006407,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.944294024957344 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08573862644689603,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.663354563061148 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08727881267314129,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.457534416113049 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0777900673407953,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.855111638084054 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07686599298399535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.009654350113124 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07659417236052497,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.055823559174314 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07803659233312664,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.814501121873036 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30756486303583724,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2513466919772327 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3089143656967891,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2371430760249496 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037592539345494926,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.601022900035606 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043839812414059334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.810316580627113 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004519268254891075,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.2747603370808 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005520230603701968,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.15185248409398 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1714959168952,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1256903241899682,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.9560619040858 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0859595397960488,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.633380103856325 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08621018296595578,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.599557796958834 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07782650647314511,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.849092748947442 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0816497686854696,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.24743212503381 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08007388194101109,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.48846659809351 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08035895884044336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.444163220003247 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31056843447494703,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.219902246957645 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.313393109741816,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1908806189894676 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03746662119201808,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.69042385420762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0448250466611641,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.308956141397356 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004599590282823514,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.4106688881293 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005588039367114167,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.95364264701493 sec\nrounds: 1"
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
          "id": "c7b4f02938e19f2c92017abb7bbd7052701b6561",
          "message": "Merge pull request #505 from OpenTrafficCam/feature/4897-add-metadata-needed-for-format-of-appendix-7\n\nfeature/4897-add-metadata-needed-for-format-of-appendix-7",
          "timestamp": "2024-04-26T15:39:24Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/c7b4f02938e19f2c92017abb7bbd7052701b6561"
        },
        "date": 1715131824098,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12815502279333463,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.803049605106935 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08884847478302663,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.25511723686941 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0881250753341763,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.34750803001225 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07936389675467384,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.600187754025683 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07881439605010948,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.688037339830771 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07647538864492708,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.076102229999378 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07611986985151271,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.1371743271593 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29363837818954114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.4055493909399956 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2987925679588955,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.346803459106013 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03718485925021967,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.892665998032317 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04420997170998212,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.619331370759756 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004587666107020085,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 217.97575862589292 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005548280109990803,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.2360335411504 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715218064938,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12671495445870692,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.891728362068534 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08692985746264235,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.503527432214469 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0879981995610756,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.36386886308901 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0786067575972416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.721552581060678 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07888828012197753,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.67615415691398 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07949164496525103,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.57993843802251 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07943825109260996,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.588393956888467 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3129114759685246,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1957920268177986 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31551307374474497,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.169440771918744 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037722164572471135,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.509613415179775 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044802639777299244,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.320113389985636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004537575343066227,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.3820155907888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005593606958513319,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.77552130795084 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715304824987,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12755785350662013,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8395800220023375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08824427461283846,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.332179956007167 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09182094376637828,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.890761508009746 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08123013771637765,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.310701768001309 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07999071449876459,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.50145102798706 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07933530817995808,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.604728246995364 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07997713790166909,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.503573224006686 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30892846345723046,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.236995350991492 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3100298545722479,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.225495820006472 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03686935916008813,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.1227930937981 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04533732357056418,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.05688208399806 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004579729655705809,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 218.35350013599964 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005587924580365131,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.957318700006 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715391452665,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11485311782782247,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.70677277998766 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08518893853503719,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.7386132190004 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08672309336650746,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.53095399599988 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07726291562285104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.942819875985151 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07690191820615416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.003576807008358 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07671990718224449,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.034426614001859 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07839804160003006,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.755420666013379 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31228390207675405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2022143740032334 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31018303758791627,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2239029180200305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.0371055711151167,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.9501309357991 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04420889105474704,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.61988428439945 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004547902197289367,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.88159740902483 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0054919788312173074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.08373169900733 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715477645004,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12560351441460552,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.961560666997684 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08889505713930544,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.249219384975731 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09062000896146104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.035090499994112 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0814577351295176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.276304986997275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08144303533186975,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.278520759020466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08005253779527839,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.491796357004205 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07959086686097865,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.564255667006364 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31421075521493214,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1825772460142616 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3135034151947146,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1897579150099773 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03659353570653999,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.327230908197816 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.045063274007758704,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.191019672201946 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004544333593819416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.0542674419994 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005535608087179707,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.64862689899746 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715563852870,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1301299778211331,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.684624378976878 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0898855933039537,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.125253372010775 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09044914409329817,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.055936571036 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07795573657869422,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.827792333031539 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07772829313707871,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.865328178973868 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07603371515424118,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.152060213964432 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07527065913555465,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.285389174008742 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29921856050539286,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.342038670030888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29816035819266923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.353899915004149 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03748632253212364,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.676396414800546 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043687282302868585,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.8899566942011 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004558070347555347,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.39108520699665 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005702258938671924,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.36909683601698 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715651010127,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12239062254844703,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.170560613041744 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08553951309677872,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.69050376600353 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08664228541875886,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.541708476026542 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07949689796036405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.57910718099447 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07957191800874208,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.56724765500985 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0793041529992448,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.609680100984406 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07854035112377848,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.73230875201989 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30229185696852673,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.308061322022695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.301194005779299,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.320119194977451 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03674439940099714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.21503184980247 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.0448648133090374,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.289182239805815 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004468529275335007,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 223.78727728599915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005457441563554386,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 183.23604354797862 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715736596955,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1308932545984063,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.6398130909656174 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08986544322466225,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.127747931983322 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08931135528099954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.196784516971093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08069873010961913,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.391768725996371 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08076998204811157,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.380837220000103 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07747745262106627,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.906980885018129 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07702807272778764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.982279895979445 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30013283123180656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3318580839550123 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2976951856436541,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3591406519990414 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03725356304000584,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.843069988396017 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044378697353433826,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.533333775796926 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0046410559376456805,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 215.46820668299915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0056969597097138985,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 175.5322226160206 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1715909370617,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13089411295114858,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.639762992039323 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08981254277746349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.134302282007411 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09240195997392904,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.822281262022443 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08213694806801401,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.174788855947554 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07969236297841878,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.548253842978738 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07978095236373728,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.534320165053941 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08032558803028293,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.449333077063784 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2960075223247656,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.378292524954304 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29222674662588527,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.422000249964185 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03679429789287837,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.178124254778957 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04555676973147416,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 21.950634469790383 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004531584972298563,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.67334191303235 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005605234937250737,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.404654076905 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1716082449452,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12484015636466497,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.010243091004668 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08983171430876351,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.131926042988198 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.09103467318297294,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 10.984825506980997 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.08190053565984591,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.209932352008764 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08231494406080314,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.14846236500307 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.08075121456949065,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.383714663999854 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.08000253120976583,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.49960451098741 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3178867092960279,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.1457748020184226 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3165977787746081,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.158581856987439 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03631014349363411,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.540513580600965 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044794070428551755,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.32438334879698 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00455905812070357,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.34355156798847 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00551489291609451,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.32718353997916 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1716168643243,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1270663578605008,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.8699037010082975 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08819492229783102,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.338521243014839 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0899646333956995,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.115479075000621 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07989872608281862,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.515844106994336 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07656238341330632,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.061244379001437 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0765495062819114,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.063441537000472 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07618932995464914,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.1251974600018 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.298455650073304,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3505815679964144 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2941745443103142,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3993423949868884 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03709321748261785,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.959106485400117 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04384292142570035,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.808699043805245 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0044984615286110755,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.29822210100247 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005574223306226335,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.39719043602236 sec\nrounds: 1"
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
          "id": "6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc",
          "message": "Merge pull request #514 from OpenTrafficCam/bug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame\n\nbug/4710-bbox-in-miovision-videos-are-completly-out-of-sync-with-background-frame",
          "timestamp": "2024-05-08T07:41:26Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/6e7f25410d03a6cde15bfe6aff375ebc8b5ed7fc"
        },
        "date": 1716255116511,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12610558228464575,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.929863070952706 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08553382405498977,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.691281326988246 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08675597865570604,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.526583130005747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07705776641812684,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.977277262019925 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07727461241437722,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.940860765986145 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07626043677742847,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.112959251971915 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07624757905071375,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.115170507051516 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29272978098831814,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.416119796980638 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30545353087197463,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2738203979679383 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03769935899404073,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.525649949593934 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043179837786832764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.15895684779389 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004456883042915507,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 224.37205337698106 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0054784038869991674,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.53491721797036 sec\nrounds: 1"
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
          "id": "7fcc2275b7f048750792fbb5c7b9d79943b3ddf0",
          "message": "Merge pull request #515 from OpenTrafficCam/feature/4995-fallback-to-video-file-name-if-relative-path-can-not-be-found\n\nFeature/4995 fallback to video file name if relative path can not be found",
          "timestamp": "2024-05-21T11:14:22Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/7fcc2275b7f048750792fbb5c7b9d79943b3ddf0"
        },
        "date": 1716341657814,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12497881523114003,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.001356055028737 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08905589161870253,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.228903352981433 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08869313172333157,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.27483019902138 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07844372407646902,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.747992420976516 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07907600246540286,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.646061622013804 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07748051091785896,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.906471422989853 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07835771770173895,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.761984771001153 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3094752782787207,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2312758730258793 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.306245757269076,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2653513600234874 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036278019822880314,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.56490031380672 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044614851202909166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.414061081409454 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0045031503889468505,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.06675629899837 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.00548867439793787,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.19335444195895 sec\nrounds: 1"
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
          "id": "7fcc2275b7f048750792fbb5c7b9d79943b3ddf0",
          "message": "Merge pull request #515 from OpenTrafficCam/feature/4995-fallback-to-video-file-name-if-relative-path-can-not-be-found\n\nFeature/4995 fallback to video file name if relative path can not be found",
          "timestamp": "2024-05-21T11:14:22Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/7fcc2275b7f048750792fbb5c7b9d79943b3ddf0"
        },
        "date": 1716428004826,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12305384462746057,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.126523824001197 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08516883261590731,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.741384368971922 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08656446667758903,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.552084110036958 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07799843539995517,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.820769992016722 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.08109869012299833,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.330655383993872 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07874151856770555,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.699780474009458 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07898073151332388,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.66131600504741 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31050053346482615,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.220606382994447 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3099805498707757,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2260088589973748 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03644560496695348,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.438150660600513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04360183631404166,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.93481386420317 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004496224561111373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.40882020199206 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005478783687615622,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.5222635199898 sec\nrounds: 1"
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
          "id": "7fcc2275b7f048750792fbb5c7b9d79943b3ddf0",
          "message": "Merge pull request #515 from OpenTrafficCam/feature/4995-fallback-to-video-file-name-if-relative-path-can-not-be-found\n\nFeature/4995 fallback to video file name if relative path can not be found",
          "timestamp": "2024-05-21T11:14:22Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/7fcc2275b7f048750792fbb5c7b9d79943b3ddf0"
        },
        "date": 1716514251690,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1277083017349269,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.830344514921308 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08887557806821099,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.251684903050773 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.089453674021561,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.178970690001734 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07825531633437458,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.778684527031146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07767698570225176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.87382602400612 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.0758337212648875,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.186745728948154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0757761598434988,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.196762703009881 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29854754247099724,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.349550265003927 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3019019360281368,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.312333843088709 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03717939231032649,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.896620354987682 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04380062747337125,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.83072315820027 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004532842376488042,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.61212743399665 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0056005331280812145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 178.55442993203178 sec\nrounds: 1"
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
          "id": "5393515cc74cfad06b6103cf596193e319d5133c",
          "message": "Merge pull request #502 from OpenTrafficCam/dependabot/pip/pandas-2.2.2\n\nBump pandas from 2.2.0 to 2.2.2",
          "timestamp": "2024-05-24T11:36:55Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/5393515cc74cfad06b6103cf596193e319d5133c"
        },
        "date": 1716600533305,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12514480594633043,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.990743143018335 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08390391150754395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.91839548398275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08958087965298983,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.163096453994513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07889928533666932,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.674386031925678 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07885086327247078,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.682169332052581 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07736120446377048,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.926375783979893 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07765571712790632,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.877351945033297 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31198585199737033,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2052735519828275 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31117269403514464,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2136495880549774 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03631682485250878,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.535446836589834 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.044568882923089775,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.43717891080305 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0045476992115242535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 219.89141178596765 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005517632845148884,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.23714064795058 sec\nrounds: 1"
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
          "id": "5393515cc74cfad06b6103cf596193e319d5133c",
          "message": "Merge pull request #502 from OpenTrafficCam/dependabot/pip/pandas-2.2.2\n\nBump pandas from 2.2.0 to 2.2.2",
          "timestamp": "2024-05-24T11:36:55Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/5393515cc74cfad06b6103cf596193e319d5133c"
        },
        "date": 1716687439239,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12222483418681743,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.181643335032277 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0848149019073892,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.790380906080827 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08679168794628264,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.521840670029633 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07752346720072696,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.899319858988747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07775732017416104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.860525513999164 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07649335233281279,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.07303144002799 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07691112015504786,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.00202100793831 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30950079147665543,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2310095080174506 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3145870531859377,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.178770359023474 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03714702647946104,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.920055110007524 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04369070028340365,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.888165982998906 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.00446961241235081,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 223.73304612201173 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005488779246452858,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.189874122967 sec\nrounds: 1"
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
          "id": "1e6391a982a4c6b99f733b6bc55a99234fb56697",
          "message": "Merge pull request #512 from OpenTrafficCam/dependabot/pip/mypy-1.10.0\n\nBump mypy from 1.8.0 to 1.10.0",
          "timestamp": "2024-05-27T11:33:20Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/1e6391a982a4c6b99f733b6bc55a99234fb56697"
        },
        "date": 1716860771732,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13349435272701118,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.490953583968803 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08828584464203827,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.32684411702212 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08819118868772274,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.33900126395747 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07917121379400141,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.630853464012034 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07854973877415457,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.730787086067721 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07631033199505471,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.104385393904522 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.0781409938741804,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.797380100004375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30525644979791844,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2759340569609776 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30293546613713457,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3010330970864743 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03928906258604975,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 25.452376162190923 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04372373663633184,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.870872366591357 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004657795513650899,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 214.69383897795342 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005818936067780494,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 171.85272158891894 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1716946454156,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12297399544601816,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.131800519069657 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08782234045225218,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.386624346952885 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08925831177664309,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.203438426018693 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07858544878901713,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.725002088933252 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07858461686006951,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.72513680101838 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07782735566269308,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.848952549975365 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07789706915924535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.837453459971584 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3030517511967497,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2997664459981024 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30800942111681634,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.246653937967494 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03625243295309515,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.584355546394363 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04430968740441137,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.568428228190168 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004536139132935207,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.45179186400492 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005512326068965909,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.41161961189937 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717033600359,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1228397547837246,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.140687041915953 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08489403042459516,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.779391259886324 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08647246507674598,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.56437484594062 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07642833494073722,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.08415263495408 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07663215130181802,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.049353084992617 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07529812384408047,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.280543378088623 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07589288962311241,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.176464949036017 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29636308891056945,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.374239361844957 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2977497597635778,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.358524960000068 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037438896293141816,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.71018910841085 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04300191136129945,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.25478027239442 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004505262905769946,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.96262924396433 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005515236210742725,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.3158968698699 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717119180690,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1258311806182952,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.947155824862421 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08351276204707817,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.974217778071761 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08593027786918717,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.637341630877927 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07647847620767295,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.075574326096103 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07888259368008198,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.677067948039621 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07836463963091798,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.76085750805214 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07870693058746069,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.705361427972093 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.31079127598265605,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2175935339182615 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.310497401986175,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.220638863975182 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.036893024762591015,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.10539475781843 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04407322207710937,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.689514241786675 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0045269241158229145,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 220.9005440371111 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005480328324818271,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.4708193980623 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717206424546,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12275291517858344,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.14644604199566 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08502606938697974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.761098768998636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08520245313893661,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.736751268996159 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07630987450391835,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.104463957002736 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07627656365786652,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.110186826001154 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07543822326422255,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.255879535994609 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07537282996794008,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.267380307006533 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2924895697648246,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.41892533400096 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.31108729494415666,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2145317930117017 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037225004304445856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.86366378419916 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04282601947061243,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.35029060280067 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.0044980375174400525,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.31917722400976 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005485741748137548,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.2907540879969 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717292132515,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12293331182223186,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.134491662000073 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0861195129676539,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.61177026599762 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08711457153219622,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.479135836998466 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07739124212141506,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.921358704013983 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07749949940311462,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.903309152985457 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07482472945574045,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.364565528987441 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07458328565041074,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.407829800999025 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29351112487852854,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.407025885011535 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29156865916612373,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.429723904002458 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.035811525703893926,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.92397085420089 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04295853610234178,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.278260637598578 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004468584213590885,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 223.78452597101568 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0055602688895079674,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 179.8474174310104 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717378334059,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12240353570059323,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.169698646990582 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08488557668785954,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.780564366985345 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08550941950350498,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.694618040986825 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07640793283540237,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.087646307016257 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07629297244201395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.107367140008137 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07445133370683485,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.431592829991132 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07494710315521148,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.342743854009314 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30707016982940644,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.256584644987015 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30528588848179655,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.275618159008445 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03745130894288073,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.701336434599945 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04345017512371746,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.01486696319771 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004507587832957473,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.84814518498024 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005494342081934075,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.00541303900536 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717465510672,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11900605663575256,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.402933667995967 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08597049021414753,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.63189831195632 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08756416666441816,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.420196618011687 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0784425459238028,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.748183886986226 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07801251715841648,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.818455761007499 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07701422284120732,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.984614569984842 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07541387400459522,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.26015952898888 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.29358180474137147,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.406205643026624 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29613128975058833,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3768805749714375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03610030984178505,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.70059327420313 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04307087938609179,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.217543134791775 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004470205425769025,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 223.70336589799263 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005473319983592678,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.70446511398768 sec\nrounds: 1"
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
          "id": "f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2",
          "message": "Merge pull request #523 from OpenTrafficCam/dependabot/pip/interrogate-1.7.0\n\nBump interrogate from 1.5.0 to 1.7.0",
          "timestamp": "2024-05-28T08:33:34Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/f5a3ca49ce92c7d52c2c9e58adc6f673cedb6ae2"
        },
        "date": 1717551071452,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12787385076433222,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.820207134005614 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08689116137649286,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.508650409989059 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0880939688107223,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.351514905050863 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07678181761547918,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.023916742997244 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.0758905683269468,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.176867983012926 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07505236113725898,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.324031180993188 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07540179992760757,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.262282876006793 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2960841640538077,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.377418050018605 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.29744790574674046,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3619332349626347 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03680872537586058,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.167471565201414 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043191549655294086,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.15267703939462 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004506315205955649,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.91079724702286 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005537764708219627,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.57827529503265 sec\nrounds: 1"
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
          "id": "2750c6fc0af2b0ca5cb0dfaab69e0a2cb4e6bdd2",
          "message": "Merge pull request #516 from OpenTrafficCam/bug/missing-metadata-when-loading-otconfig-via-cli\n\nbug/missing-metadata-when-loading-otconfig-via-cli",
          "timestamp": "2024-06-05T08:23:04Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/2750c6fc0af2b0ca5cb0dfaab69e0a2cb4e6bdd2"
        },
        "date": 1717637467712,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.13004076297582914,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.689896437979769 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0880263488680478,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.360234893974848 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08858215379549747,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.28895558702061 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07722071306556193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.94989336800063 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07672015711797911,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.034384150989354 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.075799297379088,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.19273442600388 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07598755285189758,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.160050067002885 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2978781812463192,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3570770299993455 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.2994355095958733,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.339617273013573 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037010576476726405,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.01930353959324 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04314115348595056,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.179723284998907 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004517070210587099,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.3824344939785 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005550592643779851,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 180.16094211500604 sec\nrounds: 1"
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
          "id": "7f4ca24fc6498224604e24da2ccf0c20261f2bb3",
          "message": "Merge pull request #525 from OpenTrafficCam/dependabot/pip/pytest-cov-5.0.0\n\nBump pytest-cov from 4.1.0 to 5.0.0",
          "timestamp": "2024-06-06T18:36:08Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/7f4ca24fc6498224604e24da2ccf0c20261f2bb3"
        },
        "date": 1717724033872,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12462367522791858,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.024157513980754 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08493580995565395,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.773597031948157 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.0867510250584349,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.52724131301511 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07906893328932339,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.64719224604778 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07885766692785305,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.681075144093484 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07771636469498923,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.867302838014439 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07801645417776507,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.817808890948072 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30697210966125105,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2576249389676377 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30640161709241176,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2636903469683602 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03617838373989995,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.640814669593237 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04426097125402714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 22.593268327997066 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004497938596273211,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 222.32406659098342 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.0054865219708334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 182.26483103795908 sec\nrounds: 1"
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
          "id": "26fa964b2510d2f457d154d00d68e4493d3d9975",
          "message": "Merge pull request #520 from OpenTrafficCam/dependabot/pip/matplotlib-3.9.0\n\nBump matplotlib from 3.8.2 to 3.9.0",
          "timestamp": "2024-06-07T07:26:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/26fa964b2510d2f457d154d00d68e4493d3d9975"
        },
        "date": 1717810290557,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12847123802566077,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.783843414043076 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08734383080633394,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.449005508096889 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08599781955761794,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.628201797953807 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07573221094053005,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.204421045957133 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07621329366663779,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.121070510009304 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07568569715381199,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.21253602206707 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07532340230853189,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.276086439960636 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.2979760230723197,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3559747179970145 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30086937258070334,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.323701550019905 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037456788434324914,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.697430340386926 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04298931687351214,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.261593175400048 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004514500672829462,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.50843968603294 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005515573158284016,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.30482024303637 sec\nrounds: 1"
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
          "id": "26fa964b2510d2f457d154d00d68e4493d3d9975",
          "message": "Merge pull request #520 from OpenTrafficCam/dependabot/pip/matplotlib-3.9.0\n\nBump matplotlib from 3.8.2 to 3.9.0",
          "timestamp": "2024-06-07T07:26:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/26fa964b2510d2f457d154d00d68e4493d3d9975"
        },
        "date": 1717897326926,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.1264476457992737,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 7.908411371987313 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.0855634673025974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.687230912037194 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08546071792296175,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.701282464084215 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07712191410702629,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.96648315305356 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07667847944539363,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.041468834970146 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07526668144905616,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.286091279005632 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07495437186868281,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.34144993906375 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.30500260794518985,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.278660489944741 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.311396328313378,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2113416539505124 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.037038306369695066,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.999074688204566 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.043216621687293774,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.13924506260082 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004514953078513592,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 221.48624417802785 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005515737230679768,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 181.29942710790783 sec\nrounds: 1"
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
          "id": "26fa964b2510d2f457d154d00d68e4493d3d9975",
          "message": "Merge pull request #520 from OpenTrafficCam/dependabot/pip/matplotlib-3.9.0\n\nBump matplotlib from 3.8.2 to 3.9.0",
          "timestamp": "2024-06-07T07:26:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/26fa964b2510d2f457d154d00d68e4493d3d9975"
        },
        "date": 1717983454782,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.12480204283708714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.012689354014583 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08539765142252724,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.709923907066695 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08547167999973443,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.69978172890842 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.0760113254595621,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.155934249982238 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07541441213618295,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.260064909001812 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07550696762846226,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.243810888030566 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07608089401197336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.143904432072304 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3068714141926801,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.2586938820313662 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.3065307185893129,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.26231577899307 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03705592337340611,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 26.986238878010774 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.04276922092267171,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.381300346995705 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004426668741168193,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 225.903508591 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005378847584306336,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 185.91342928505037 sec\nrounds: 1"
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
          "id": "26fa964b2510d2f457d154d00d68e4493d3d9975",
          "message": "Merge pull request #520 from OpenTrafficCam/dependabot/pip/matplotlib-3.9.0\n\nBump matplotlib from 3.8.2 to 3.9.0",
          "timestamp": "2024-06-07T07:26:31Z",
          "url": "https://github.com/OpenTrafficCam/OTAnalytics/commit/26fa964b2510d2f457d154d00d68e4493d3d9975"
        },
        "date": 1718069900682,
        "tool": "pytest",
        "benches": [
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTrackParser::test_load_15min",
            "value": 0.11997246599319714,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 8.335245855967514 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min",
            "value": 0.08202831068518764,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 12.19091301097069 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkTracksIntersectingSections::test_15min_filtered",
            "value": 0.08434446720456354,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 11.856142236036249 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min",
            "value": 0.07579303227208763,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.193824946996756 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCreateEvents::test_15min_filtered",
            "value": 0.07604033122822298,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.150915886973962 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min",
            "value": 0.07621733030556259,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.120375589001924 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkExportCounting::test_15min_filtered",
            "value": 0.07682944438296983,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 13.015843183966354 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min",
            "value": 0.3018945380831129,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.312415012042038 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestBenchmarkCuttingSection::test_15min_filtered",
            "value": 0.30274524727492763,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 3.3031071800505742 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min",
            "value": 0.03595186399990856,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 27.814969482598826 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_15min_filtered",
            "value": 0.042557160466502535,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 23.497808336792513 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours",
            "value": 0.004410004282776974,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 226.75714939902537 sec\nrounds: 1"
          },
          {
            "name": "tests/benchmark_otanalytics.py::TestPipelineBenchmark::test_2hours_filtered",
            "value": 0.005375301763047514,
            "unit": "iter/sec",
            "range": "stddev: 0",
            "extra": "mean: 186.03606719803065 sec\nrounds: 1"
          }
        ]
      }
    ]
  }
}