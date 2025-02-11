from pathlib import Path
from typing import Callable, Literal

from nicegui import ui
from nicegui.events import UploadEventArguments
from OTCloud.adapter.nicegui_mapping.otcloud_mapper import NiceguiOtcloudJobConfig
from OTCloud.plugin_file_picker.local_file_picker import LocalFilePicker
from OTCloud.plugin_webserver.nicegui.constants import Alignment
from OTCloud.plugin_webserver.nicegui.elements.table import MissingInstanceError
from OTCloud.plugin_webserver.pages.create_job_config.otcloud.settings import (
    OtcloudConfigSettings,
)
from OTCloud.plugin_webserver.pages.create_job_config.otvision.settings import (
    OtvisionConfigSettings,
)

LABEL_CREATE_OTCLOUD_JOB_CONFIG = "Create OTCloud Job Config"
LABEL_UPLOAD_EXISTING_OTCLOUD_JOB_CONFIG = "Upload Existing OTCloud Job Config"
LABEL_LOAD_OTCONFIG = "Load OTConfig"
LABEL_CREATE_JOB = "Create Job"

FILETYPE_OTCONFIG = ".otconfig"


class CreateJobConfigPage:
    """The create job config page.

    Args:
        create_job(Callable[[], None]): the callback to register to the create job
            button.
        upload_existing_job_config(Callable[[UploadEventArguments], None]): the callback
            to register to upload an existing job config element.

    """

    @property
    def _otcloud_settings(self) -> OtcloudConfigSettings:
        if self.__otcloud_settings:
            return self.__otcloud_settings
        raise MissingInstanceError(
            f"{self.__otcloud_settings.__class__.__name__} "
            "has not been instantiated yet"
        )

    @property
    def _otvision_settings(self) -> OtvisionConfigSettings:
        if self.__otvision_settings:
            return self.__otvision_settings
        raise MissingInstanceError(
            f"{self.__otcloud_settings.__class__.__name__} "
            "has not been instantiated yet"
        )

    def __init__(
        self,
        create_job: Callable[[], None],
        upload_existing_job_config: Callable[[UploadEventArguments], None],
        load_otconfig: Callable[[str], None],
        file_picker_start: Path,
    ) -> None:
        self._create_job = create_job
        self._upload_existing_job_config = upload_existing_job_config
        self._load_otconfig = load_otconfig
        self._file_picker_start = file_picker_start
        self.__otcloud_settings: OtcloudConfigSettings | None = None
        self.__otvision_settings: OtvisionConfigSettings | None = None

    def build(self, job_config: NiceguiOtcloudJobConfig) -> None:
        """Builds the create job config page.

        Args:
            job_config (NiceguiOtcloudJobConfig): the job config to prefill the fields
                with.

        """
        self.__configure_ui_elements(job_config)
        self.__build_ui()

    def __configure_ui_elements(self, job_config: NiceguiOtcloudJobConfig) -> None:
        self.__otcloud_settings = OtcloudConfigSettings(
            project_name=job_config.project_name,
            copy_files_before_processing=job_config.copy_files_before_processing,
            otconfig_file=job_config.otconfig_file,
        )
        self.__otvision_settings = OtvisionConfigSettings(job_config.otvision_config)

    def __build_ui(self) -> None:
        with ui.column(align_items=Alignment.stretch):
            ui.label(LABEL_CREATE_OTCLOUD_JOB_CONFIG).classes(
                "text-2xl font-bold leading-7 sm:truncate sm:text-3xl sm:tracking-tight"
            )
            self._otcloud_settings.build()
            self._otvision_settings.build()
            with ui.card(align_items="stretch"):
                with ui.column():
                    ui.upload(
                        label=LABEL_UPLOAD_EXISTING_OTCLOUD_JOB_CONFIG,
                        on_upload=self._upload_existing_job_config,
                        auto_upload=True,
                    )
                with ui.row():
                    ui.button(
                        LABEL_LOAD_OTCONFIG,
                        icon="file_upload",
                        on_click=self._on_load_otconfig_button_clicked,
                    )
                    ui.button(
                        LABEL_CREATE_JOB,
                        icon="send",
                        on_click=self._create_job,
                    )

    async def _on_load_otconfig_button_clicked(self) -> None:
        picker = LocalFilePicker(
            directory=self._file_picker_start,
            multiple=False,
            show_hidden_files=False,
            show_files_only_of_type=FILETYPE_OTCONFIG,
        )
        otconfig_file = await picker
        picker.clear()
        if otconfig_file:
            self._load_otconfig(otconfig_file[0])

    def validate(self) -> bool:
        """Validate otcloud settings and otvision settings for invalid inputs.

        Returns:
            bool: `True`, if all settings are valid. Otherwise, `False`.

        """
        valid_otcloud = self._otcloud_settings.validate()
        valid_otvision = self._otvision_settings.validate()
        return valid_otcloud and valid_otvision

    def update_with_config(self, job_config: NiceguiOtcloudJobConfig) -> None:
        """Update form fields with OTCloud job config.

        This also refreshes the respective UI elements.

        Args:
            job_config (NiceguiOtcloudJobConfig): job config to update the page with.

        """
        self._otcloud_settings.update(job_config)
        self._otvision_settings.update(job_config.otvision_config)

    def get_config(self) -> NiceguiOtcloudJobConfig:
        """Get the current OTCloud job config filled out by the user.

        Returns:
            NiceguiOtcloudJobConfig: The current OTCloud job config filled out by the
                user.

        """
        otcloud_settings = self._otcloud_settings.get_config()
        return NiceguiOtcloudJobConfig(
            project_name=otcloud_settings.project_name,
            copy_files_before_processing=otcloud_settings.copy_files_before_processing,
            otvision_config=self._otvision_settings.get_config(),
            otconfig_file=otcloud_settings.otconfig,
        )

    def display_notify_msg(
        self,
        msg: str,
        level: Literal["positive", "negative", "warning", "info", "ongoing"],
        show_close_button: bool = False,
        progress: bool = True,
        timeout: int = 3,
    ) -> None:
        """Display notification message to the user.

        Args:
            msg (str): the message to display.
            level (Literal["positive", "negative", "warning", "info", "ongoing"]):
                configures the color of the notification message.
            show_close_button (bool): whether to show the close button.
            progress (bool): whether to show the progress until the notification is
                going to disappear. If show_close_button is `True`, progress
                is implicitly set to `False`.
            timeout (int): the time in seconds for how long the notification should
                be displayed. If show_close_button is `True`, timeout is set to 0.

        """
        close_button: bool | str = False
        if show_close_button:
            progress = False
            timeout = 0
            close_button = "Ok"

        ui.notify(
            msg,
            position="top",
            type=level,
            close_button=close_button,
            multi_line=True,
            timeout=timeout * 1000,
            progress=progress,
        )
