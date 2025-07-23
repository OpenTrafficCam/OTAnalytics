from enum import Enum


class EventTypeParseError(Exception):
    pass


class EventType(Enum):
    """Enum defining all event types."""

    SECTION_ENTER = "section-enter"
    SECTION_LEAVE = "section-leave"
    ENTER_SCENE = "enter-scene"
    LEAVE_SCENE = "leave-scene"

    def serialize(self) -> str:
        return self.value

    @staticmethod
    def parse(event_type: str) -> "EventType":
        match event_type:
            case EventType.SECTION_ENTER.value:
                return EventType.SECTION_ENTER
            case EventType.SECTION_LEAVE.value:
                return EventType.SECTION_LEAVE
            case EventType.ENTER_SCENE.value:
                return EventType.ENTER_SCENE
            case EventType.LEAVE_SCENE.value:
                return EventType.LEAVE_SCENE
            case _:
                raise EventTypeParseError(
                    f"Unable to parse not existing event type '{event_type}'"
                )
