from dataclasses import dataclass


@dataclass(frozen=True)
class FlowDto:
    flow_id: str | None
    name: str
    start_section: str
    end_section: str
    distance: float | None

    def derive_name(self, new_name: str) -> "FlowDto":
        return FlowDto(
            flow_id=self.flow_id,
            name=new_name,
            start_section=self.start_section,
            end_section=self.end_section,
            distance=self.distance,
        )
