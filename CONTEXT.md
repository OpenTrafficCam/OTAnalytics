# OTAnalytics

Traffic analysis on road user trajectories: OTAnalytics loads Tracks recorded by
OTVision, lets a user define Sections and Flows over them, and counts the road
users crossing those Sections.

## Language

### Obtaining input files

**Transfer Mode**:
Where an OTAnalytics instance obtains its Track and Video files — the local
filesystem, or an S3 bucket. Fixed for the lifetime of the process by the
startup configuration; it is not something a user switches while working.
_Avoid_: storage backend, data source (both suggest a per-load choice).

**Startup Configuration**:
The file naming the Transfer Mode and, in S3 mode, the S3 settings. Distinct
from an **otconfig**, which is a per-project file a user saves and shares —
credentials belong in the Startup Configuration, never in an otconfig.
_Avoid_: config file (ambiguous between the two).

**Key Prefix**:
The single S3 prefix an instance reads from, covering one camera or site. Fixed
at startup, so a user chooses only *when*, never *where*.
_Avoid_: path, folder (S3 has neither).

**User Source**:
The local directory that downloaded objects are written into, mirroring their S3
keys, so that a Track file and its Video land side by side. Named after
OTCloud's `S3_USER_SOURCE` for cross-repo consistency, though the name conveys
little on its own. Its contents do not survive a restart.
_Avoid_: cache (implies reuse across runs, which there is none of).

**Load Window**:
The start and end time a user selects to decide which Tracks and Videos to load.
Bounded by a configured maximum duration, because continuous processing produces
far more data than can be held at once.
_Avoid_: time range, date range (`DateRange` already means the filter applied to
already-loaded Tracks, which is a different thing).
