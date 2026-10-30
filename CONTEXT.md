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

### Placing Tracks in the world

**Geo-only Track File**:
A Track file whose positions are given only in geo coordinates, with no image
coordinates and no Video. OTFusion produces these, because it fuses several
cameras into one world view rather than into any single camera's image.
_Avoid_: fusion video, bird's-eye-view file (there is no video or rendered image).

**Orthophoto**:
A georeferenced aerial image of a site, shown as the background for Tracks that
have no Video. Its own georeference is what relates a point on the image to a
point in the world.
_Avoid_: map, GeoTIFF (a file format, not the concept), bird's-eye view (the image
OTFusion used to render, which no longer exists).

### Exports

**Traffic Statistics**:
A per-day JSON file of counts, peak hours and speeds per flow and class group,
written to `{save_stem}.traffic_statistics_{YYYY-MM-DD}.json` and updated chunk by
chunk. Days are cut in the configured timezone, and a road user is counted at
most once per day. Speed is flow distance divided by the time between the road
user's start and end event; implausible speeds are counted but left out of the
speed figures. After a restart, a day is rebuilt from road user assignment files;
only coverage and as_of are read from the day file.
_Avoid_: counts (the CSV counting export, which has no speeds and no peak hours),
track statistics (per-track metrics such as length and duration), report, summary
(too vague to tell the exports apart).

**Geo Track Export**:
A bz2-compressed JSON file with one reduced trajectory point per Detection (track
ID, class, geo coordinate, time), written to
`{save_stem}_{timestamp}.geo_tracks.json.bz2` for each chunk. Detections without a
geo coordinate are dropped; if none remain, no file is written.
_Avoid_: track export (the full `.ottrk`/CSV Track export), GeoJSON, shapefile
(it is neither), geo file (does not say it holds Tracks).
