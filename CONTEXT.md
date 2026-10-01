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
The environment variables naming the Transfer Mode and, in S3 mode, the bucket
and credentials. Fixed for the lifetime of the process. Deliberately not a file.
Says what a deployment may authenticate to, never which project it holds: the
Key Prefix comes from the **otconfig** instead, because that is per-project and
varies per lease. Credentials must never travel in an otconfig, since users save
and share those files.
_Avoid_: config file (there isn't one, and it invites confusion with otconfig).

**Key Prefix**:
The S3 prefix a project's Tracks and Videos live under, covering one camera or
site. A property of the project, declared by its otconfig, and required there in
S3 mode — so opening a different project moves where an instance reads from,
within the one configured bucket. Until a project is loaded there is no Key
Prefix and nothing can be listed.
_Avoid_: path, folder (S3 has neither); startup configuration (it is per-project,
unlike the bucket and credentials).

**User Source**:
The local directory that downloaded objects are written into, mirroring their S3
keys, so that a Track file and its Video land side by side. Named after
OTCloud's `S3_USER_SOURCE` for cross-repo consistency, though the name conveys
little on its own. Its contents do not survive a restart.
_Avoid_: cache (implies reuse across runs, which there is none of).

**Load Window**:
The start and end time a user selects to decide which Tracks and Videos to load.
Bounded by a configured maximum duration, because continuous processing produces
far more data than can be held at once. An over-long selection is _clamped_ —
its end snaps to the maximum and the user is told — never rejected.
_Avoid_: time range, date range (`DateRange` already means the filter applied to
already-loaded Tracks, which is a different thing).

**Track File Provider** / **Video File Provider**:
What a request for input files is asked of. Each implementation owns its own way
of asking the user, so nothing downstream knows where files came from: the local
one opens a file chooser, the S3 one asks for a Load Window and downloads. This
is the seam that makes the Transfer Mode interchangeable.
_Avoid_: file loader, importer (both suggest they also parse, which they do not —
they only obtain paths).
