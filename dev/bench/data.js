window.BENCHMARK_DATA = {
  "lastUpdate": 1700875105191,
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
      }
    ]
  }
}