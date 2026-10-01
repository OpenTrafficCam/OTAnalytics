from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

from OTAnalytics.application.orthophoto import (
    VIDEOS_BESIDE_ORTHOPHOTO,
    AddVideoFiles,
    ChooseOrthophoto,
    CurrentOrthophotoGeoreference,
    CurrentOrthophotoImage,
    LocalObtainOrthophoto,
    ProvideOrthophoto,
    ResolveMissingOrthophoto,
)
from OTAnalytics.application.state import CurrentOrthophoto
from OTAnalytics.domain.orthophoto import (
    MixedTrackFiles,
    Orthophoto,
    OrthophotoLocked,
    OrthophotoNotFound,
    OrthophotoRequired,
)
from OTAnalytics.domain.track import TrackImage

ORTHOPHOTO_FILE = Path("site/map.tiff")
CRS = "EPSG:25833"
PICKED_FILE = Path("picked/map.tiff")
VIDEO_FILES = [Path("site/camera.mp4")]


@dataclass
class Given:
    current_orthophoto: CurrentOrthophoto
    read_georeference: Mock


def create_given() -> Given:
    return Given(current_orthophoto=CurrentOrthophoto(), read_georeference=Mock())


def setup_default(given: Given) -> Given:
    given.current_orthophoto.set(Orthophoto(file=ORTHOPHOTO_FILE))
    return given


def create_target(given: Given) -> CurrentOrthophotoGeoreference:
    return CurrentOrthophotoGeoreference(
        given.current_orthophoto, given.read_georeference
    )


class TestCurrentOrthophotoGeoreference:
    def test_reads_the_current_orthophoto_in_the_requested_crs(self) -> None:
        given = setup_default(create_given())
        target = create_target(given)

        actual = target.for_crs(CRS)

        given.read_georeference.assert_called_once_with(ORTHOPHOTO_FILE, CRS)
        assert actual == given.read_georeference.return_value

    def test_reads_each_orthophoto_only_once(self) -> None:
        given = setup_default(create_given())
        target = create_target(given)

        target.for_crs(CRS)
        target.for_crs(CRS)

        given.read_georeference.assert_called_once()

    def test_refuses_without_an_orthophoto(self) -> None:
        given = create_given()
        target = create_target(given)

        with pytest.raises(OrthophotoRequired):
            target.for_crs(CRS)


class TestCurrentOrthophoto:
    def test_reset_forgets_the_orthophoto(self) -> None:
        given = setup_default(create_given())

        given.current_orthophoto.reset()

        assert given.current_orthophoto.get() is None


@dataclass
class GivenChoose:
    current_orthophoto: CurrentOrthophoto
    section_repository: Mock
    track_repository: Mock
    video_repository: Mock


def create_given_choose() -> GivenChoose:
    return GivenChoose(
        current_orthophoto=CurrentOrthophoto(),
        section_repository=Mock(),
        track_repository=Mock(),
        video_repository=Mock(),
    )


def setup_default_choose(given: GivenChoose) -> GivenChoose:
    given.section_repository.get_all.return_value = []
    given.track_repository.get_all.return_value.empty = True
    given.video_repository.get_all.return_value = []
    return given


def setup_with_sections(given: GivenChoose) -> GivenChoose:
    given.section_repository.get_all.return_value = [Mock()]
    return given


def setup_with_tracks(given: GivenChoose) -> GivenChoose:
    given.track_repository.get_all.return_value.empty = False
    return given


def setup_with_videos(given: GivenChoose) -> GivenChoose:
    given.video_repository.get_all.return_value = [Mock()]
    return given


def create_target_choose(given: GivenChoose) -> ChooseOrthophoto:
    return ChooseOrthophoto(
        given.current_orthophoto,
        given.section_repository,
        given.track_repository,
        given.video_repository,
    )


class TestChooseOrthophoto:
    def test_choose_sets_the_orthophoto(self) -> None:
        given = setup_default_choose(create_given_choose())

        create_target_choose(given).choose(PICKED_FILE)

        assert given.current_orthophoto.get() == Orthophoto(file=PICKED_FILE)

    def test_choose_is_refused_when_sections_exist(self) -> None:
        given = setup_with_sections(setup_default_choose(create_given_choose()))

        with pytest.raises(OrthophotoLocked):
            create_target_choose(given).choose(PICKED_FILE)

    def test_choose_is_refused_when_tracks_exist(self) -> None:
        given = setup_with_tracks(setup_default_choose(create_given_choose()))

        with pytest.raises(OrthophotoLocked):
            create_target_choose(given).choose(PICKED_FILE)

    def test_choose_is_refused_when_videos_exist(self) -> None:
        given = setup_with_videos(setup_default_choose(create_given_choose()))

        with pytest.raises(OrthophotoLocked):
            create_target_choose(given).choose(PICKED_FILE)


@dataclass
class GivenAddVideos:
    current_orthophoto: CurrentOrthophoto
    load_video_files: Mock


def create_given_add_videos() -> GivenAddVideos:
    return GivenAddVideos(
        current_orthophoto=CurrentOrthophoto(), load_video_files=Mock()
    )


def setup_add_videos_with_orthophoto(given: GivenAddVideos) -> GivenAddVideos:
    given.current_orthophoto.set(Orthophoto(file=ORTHOPHOTO_FILE))
    return given


def create_target_add_videos(given: GivenAddVideos) -> AddVideoFiles:
    return AddVideoFiles(given.load_video_files, given.current_orthophoto)


class TestAddVideoFiles:
    def test_loads_the_videos_of_a_camera_project(self) -> None:
        given = create_given_add_videos()

        create_target_add_videos(given).add(VIDEO_FILES)

        given.load_video_files.assert_called_once_with(VIDEO_FILES)

    def test_refuses_videos_beside_an_orthophoto(self) -> None:
        given = setup_add_videos_with_orthophoto(create_given_add_videos())

        with pytest.raises(MixedTrackFiles, match=VIDEOS_BESIDE_ORTHOPHOTO):
            create_target_add_videos(given).add(VIDEO_FILES)

    def test_loads_nothing_beside_an_orthophoto(self) -> None:
        given = setup_add_videos_with_orthophoto(create_given_add_videos())

        with pytest.raises(MixedTrackFiles):
            create_target_add_videos(given).add(VIDEO_FILES)

        given.load_video_files.assert_not_called()


@dataclass
class GivenResolve:
    provide_orthophoto: AsyncMock
    choose_orthophoto: Mock


def create_given_resolve() -> GivenResolve:
    return GivenResolve(
        provide_orthophoto=AsyncMock(spec=ProvideOrthophoto),
        choose_orthophoto=Mock(spec=ChooseOrthophoto),
    )


def setup_default_resolve(given: GivenResolve) -> GivenResolve:
    given.provide_orthophoto.provide.return_value = PICKED_FILE
    return given


def setup_with_nothing_provided(given: GivenResolve) -> GivenResolve:
    given.provide_orthophoto.provide.return_value = None
    return given


def create_target_resolve(given: GivenResolve) -> ResolveMissingOrthophoto:
    return ResolveMissingOrthophoto(given.provide_orthophoto, given.choose_orthophoto)


class TestResolveMissingOrthophoto:
    async def test_chooses_the_provided_file(self) -> None:
        given = setup_default_resolve(create_given_resolve())

        await create_target_resolve(given).resolve()

        given.choose_orthophoto.choose.assert_called_once_with(PICKED_FILE)

    async def test_refuses_when_nothing_is_provided(self) -> None:
        given = setup_with_nothing_provided(create_given_resolve())

        with pytest.raises(OrthophotoRequired):
            await create_target_resolve(given).resolve()


@dataclass
class GivenImage:
    current_orthophoto: CurrentOrthophoto
    read_image: Mock


def create_given_image() -> GivenImage:
    return GivenImage(
        current_orthophoto=CurrentOrthophoto(),
        read_image=Mock(return_value=Mock(spec=TrackImage)),
    )


def setup_image_with_orthophoto(given: GivenImage) -> GivenImage:
    given.current_orthophoto.set(Orthophoto(file=ORTHOPHOTO_FILE))
    return given


def create_target_image(given: GivenImage) -> CurrentOrthophotoImage:
    return CurrentOrthophotoImage(given.current_orthophoto, given.read_image)


class TestCurrentOrthophotoImage:
    def test_reads_the_image_once_per_file(self) -> None:
        given = setup_image_with_orthophoto(create_given_image())
        target = create_target_image(given)

        target.get()
        actual = target.get()

        assert actual == given.read_image.return_value
        given.read_image.assert_called_once_with(ORTHOPHOTO_FILE)

    def test_no_orthophoto_yields_no_image(self) -> None:
        given = create_given_image()

        assert create_target_image(given).get() is None


DECLARED_ORTHOPHOTO = Path("map.tiff")


@dataclass
class GivenLocalObtain:
    base_folder: Path


def create_given_local_obtain(tmp_path: Path) -> GivenLocalObtain:
    return GivenLocalObtain(base_folder=tmp_path)


def setup_with_orthophoto_on_disk(given: GivenLocalObtain) -> GivenLocalObtain:
    (given.base_folder / DECLARED_ORTHOPHOTO).touch()
    return given


def create_target_local_obtain() -> LocalObtainOrthophoto:
    return LocalObtainOrthophoto()


class TestLocalObtainOrthophoto:
    async def test_finds_the_orthophoto_next_to_the_otconfig(
        self, tmp_path: Path
    ) -> None:
        given = setup_with_orthophoto_on_disk(create_given_local_obtain(tmp_path))

        actual = await create_target_local_obtain().obtain(
            DECLARED_ORTHOPHOTO, given.base_folder
        )

        assert actual == given.base_folder / DECLARED_ORTHOPHOTO

    async def test_reports_a_missing_orthophoto(self, tmp_path: Path) -> None:
        given = create_given_local_obtain(tmp_path)

        with pytest.raises(OrthophotoNotFound):
            await create_target_local_obtain().obtain(
                DECLARED_ORTHOPHOTO, given.base_folder
            )
