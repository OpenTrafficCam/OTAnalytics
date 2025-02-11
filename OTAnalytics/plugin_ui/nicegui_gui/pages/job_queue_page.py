from pathlib import Path
from typing import Literal

from nicegui import ui
from OTCloud.adapter.nicegui_mapping.otcloud_state_mapper import NiceguiOtcloudState
from OTCloud.application.otvision import OTCLOUD_JOB_CONFIG
from OTCloud.application.use_cases.load_otcloud_job_config import LoadOtcloudJobConfig
from OTCloud.application.use_cases.save_otcloud_job_config import SaveOtcloudJobConfig
from OTCloud.plugin_webserver.endpoints import ENDPOINT_CREATE_JOB_CONFIG_PAGE
from OTCloud.plugin_webserver.nicegui.elements.table import CustomTable, TableObserver


def create_table_column(
    name: str, label: str, field: str, alignment: str = "left", style: str = ""
) -> dict:
    """Helper function to configure columns of NiceGUI's `ui.table` element.

    Args:
        name (str): The identifier to access the column of `ui.table` instance.
        label (str): The column label to be displayed.
        field (str): the field name of the row dict corresponding to the column.
        alignment (str): alignment settings for table column.
        style (str): style settings for table column.

    """
    return dict(name=name, label=label, field=field, align=alignment, style=style)


WORKER_TABLE_TITLE = "Currently Processing"
WORKER_COLUMNS = [
    create_table_column("worker_id", "Worker ID", "id"),
    create_table_column("worker_type", "Worker Type", "type"),
    create_table_column("current_job", "Job", "current_task"),
]

FINISHED_TABLE_TITLE = "Finished"
FINISHED_COLUMNS = [create_table_column("job", "Job", "name")]

FAILED_TABLE_TITLE = "Failed"
FAILED_COLUMNS = [
    create_table_column("job", "Job", "name"),
    create_table_column(
        "error_message", "Error Message", "error_msg", style="text-wrap: wrap"
    ),
    create_table_column("failed_operation", "Failed Step", "operation"),
]
TASK_COLUMNS = [create_table_column("job_name", "Job", "name")]
ALIGN_CENTER: Literal["center"] = "center"
ALIGN_START: Literal["start"] = "start"

FAILED_TASK_TABLE_HEADER_TEMPLATE = r"""
    <q-tr :props="props">
        <q-th auto-width />
        <q-th v-for="col in props.cols" :key="col.name" :props="props">
            {{ col.label }}
        </q-th>
    </q-tr>
"""
FAILED_TASK_TABLE_BODY_TEMPLATE = r"""
    <q-tr :props="props">
        <q-td auto-width>
            <q-btn size="sm" color="accent" round dense
                @click="$parent.$emit('rerun-failed-task', {row: props.row})"
                :icon="'refresh'" />
        </q-td>
        <q-td v-for="col in props.cols" :key="col.name" :props="props">
            {{ col.value }}
        </q-td>
    </q-tr>
"""
RERUN_FAILED_TASK = "rerun-failed-task"
ROW = "row"
COLUMN_JOB = "job"

LABEL_OTCLOUD_JOB_QUEUE = "OTCloud Job Queue"
LABEL_BUTTON_CREATE_NEW_JOB_CONFIG = "Create New Job Config"
LABEL_UNDISTRIBUTED_JOBS = "Undistributed Jobs"
LABEL_CONVERT_JOBS = "Convert Jobs"
LABEL_DETECT_JOBS = "Detect Jobs"
LABEL_TRACK_JOBS = "Track Jobs"

MARKER_CREATE_NEW_JOB_CONFIG_BUTTON = "marker-create-new-job-config-button"
MARKER_WORKER_TABLE = "marker-worker-table"
MARKER_FINISHED_TASK_TABLE = "marker-finished-task-table"
MARKER_UNDISTRIBUTED_TASK_TABLE = "marker-undistributed-task-table"
MARKER_CONVERT_TASK_TABLE = "marker-convert-task-table"
MARKER_DETECT_TASK_TABLE = "marker-detect-task-table"
MARKER_TRACK_TASK_TABLE = "marker-track-task-table"
MARKER_FAILED_TASK_TABLE = "marker-failed-task-table"
MARKER_NUM_UNDISTRIBUTED_JOBS = "marker-num-undistributed-jobs"
MARKER_NUM_CONVERT_JOBS = "marker-num-convert-jobs"
MARKER_NUM_DETECT_JOBS = "marker-num-detect-jobs"
MARKER_NUM_TRACK_JOBS = "marker-num-track-jobs"


def create_pagination_options(rows_per_page: int = 5, page: int = 1) -> dict:
    return {"rowsPerPage": rows_per_page, "page": page}


PAGINATION_FIVE_ROWS = create_pagination_options(rows_per_page=5)


class JobQueuePage:
    """Class to manage and display job queues in OTCloud.

    Args:
        load_otcloud_job_config (LoadOtcloudJobConfig): use case to load OTCloud job
            config.
        save_otcloud_job_config (SaveOtcloudJobConfig): use case to save OTCloud job
            config.

    """

    def __init__(
        self,
        load_otcloud_job_config: LoadOtcloudJobConfig,
        save_otcloud_job_config: SaveOtcloudJobConfig,
    ) -> None:
        """
        Args:
            load_otcloud_job_config: Configuration object for loading Otcloud job.
            save_otcloud_job_config: Configuration object for saving Otcloud job.
        """
        self._load_otcloud_job_config = load_otcloud_job_config
        self._save_otcloud_job_config = save_otcloud_job_config
        self._worker_table = CustomTable(
            columns=WORKER_COLUMNS,
            rows=[],
            title=WORKER_TABLE_TITLE,
            marker=MARKER_WORKER_TABLE,
        )
        self._finished_task_table = CustomTable(
            columns=FINISHED_COLUMNS,
            rows=[],
            title=FINISHED_TABLE_TITLE,
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_FINISHED_TASK_TABLE,
        )
        self.__init_failed_task_table()
        self._undistributed_task_table = CustomTable(
            columns=TASK_COLUMNS,
            rows=[],
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_UNDISTRIBUTED_TASK_TABLE,
        )
        self._convert_task_table = CustomTable(
            columns=TASK_COLUMNS,
            rows=[],
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_CONVERT_TASK_TABLE,
        )
        self._detect_task_table = CustomTable(
            columns=TASK_COLUMNS,
            rows=[],
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_DETECT_TASK_TABLE,
        )
        self._track_task_table = CustomTable(
            columns=TASK_COLUMNS,
            rows=[],
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_TRACK_TASK_TABLE,
        )

    def __init_failed_task_table(self) -> None:
        self._failed_task_table = CustomTable(
            columns=FAILED_COLUMNS,
            rows=[],
            title=FAILED_TABLE_TITLE,
            header_slot=FAILED_TASK_TABLE_HEADER_TEMPLATE,
            body_slot=FAILED_TASK_TABLE_BODY_TEMPLATE,
            observers=[
                TableObserver(
                    RERUN_FAILED_TASK,
                    lambda event: self._on_rerun_failed_task(
                        event.args[ROW][OTCLOUD_JOB_CONFIG]
                    ),
                )
            ],
            pagination=PAGINATION_FIVE_ROWS,
            marker=MARKER_FAILED_TASK_TABLE,
        )

    def build(self) -> None:
        """Builds the UI layout for the OTCloud Job Queue interface."""

        with ui.grid():
            ui.label(LABEL_OTCLOUD_JOB_QUEUE).classes(
                "text-2xl font-bold leading-7 sm:truncate sm:text-3xl sm:tracking-tight"
            )
            with ui.grid():
                with ui.row():
                    ui.button(
                        text=LABEL_BUTTON_CREATE_NEW_JOB_CONFIG,
                        on_click=lambda: ui.navigate.to(
                            ENDPOINT_CREATE_JOB_CONFIG_PAGE
                        ),
                    ).mark(MARKER_CREATE_NEW_JOB_CONFIG_BUTTON)
                    ui.space()
                self._worker_table.build()
                with ui.card(align_items=ALIGN_START):
                    with ui.row():
                        self._create_queue_size_label(
                            queue_table=self._undistributed_task_table,
                            text=LABEL_UNDISTRIBUTED_JOBS,
                            marker=MARKER_NUM_UNDISTRIBUTED_JOBS,
                        )
                        self._create_queue_size_label(
                            queue_table=self._convert_task_table,
                            text=LABEL_CONVERT_JOBS,
                            marker=MARKER_NUM_CONVERT_JOBS,
                        )
                        self._create_queue_size_label(
                            queue_table=self._detect_task_table,
                            text=LABEL_DETECT_JOBS,
                            marker=MARKER_NUM_DETECT_JOBS,
                        )
                        self._create_queue_size_label(
                            queue_table=self._track_task_table,
                            text=LABEL_TRACK_JOBS,
                            marker=MARKER_NUM_TRACK_JOBS,
                        )
                self._finished_task_table.build()
                self._failed_task_table.build()

    def _create_queue_size_label(
        self, queue_table: CustomTable, text: str, marker: str
    ) -> None:
        with ui.column(align_items=ALIGN_CENTER):
            with ui.label() as undistributed_label:
                undistributed_label.mark(marker)

            queue_table.build()
            undistributed_label.bind_text_from(
                target_object=queue_table,
                target_name="size",
                backward=lambda amount: f"{text}: {amount}",
            )

    def update(self, otcloud_state: NiceguiOtcloudState) -> None:
        """Refreshes the UI with current OTCloud state.

        Args:
            otcloud_state (NiceguiOtcloudState): contains latest state for various task
            queues and worker states.

        """
        self._undistributed_task_table.update(otcloud_state.task_queue)
        self._convert_task_table.update(otcloud_state.convert_queue)
        self._detect_task_table.update(otcloud_state.detect_queue)
        self._track_task_table.update(otcloud_state.track_queue)
        self._finished_task_table.update(list(reversed(otcloud_state.finished_tasks)))
        self._failed_task_table.update(list(reversed(otcloud_state.failed_tasks)))
        self._worker_table.update(otcloud_state.current_worker_state)

    def _on_rerun_failed_task(self, task_name: str) -> None:
        """Rerun a previously failed task.

        Args:
            task_name: The name of the task that failed and needs to be rerun.

        """
        job_config = self._load_otcloud_job_config.from_file(Path(task_name))
        self._save_otcloud_job_config.from_config(job_config)
