import logging
from structures.plugin_stage import PluginStage


logger = logging.getLogger("StageManager")


class StageManager:
    stage_no: int = 0

    def __init__(self) -> None:
        logger.info("StageManager initialized")

    async def reset_stage(self) -> None:
        logger.info("Reset stage to 0")
        self.stage_no = 0

    async def next_stage(self) -> None:
        logger.info(f"Next stage to {self.stage_no + 1}")
        self.stage_no += 1

    async def get_stage(self) -> PluginStage:
        return PluginStage(self.stage_no)

    async def is_last_stage(self) -> bool:
        return self.stage_no == PluginStage.COMPLETE.value
