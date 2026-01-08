from abc import ABC, abstractmethod

from pydantic import BaseModel

from config import Config
from managers.stage_manager import StageManager
from model.context import Context


class StageResult(BaseModel):
    """
    阶段结果
    """

    success: bool
    context: Context


class AStageProcessor(ABC):
    @abstractmethod
    async def process(
        self, stage_manager: StageManager, context: Context, config: Config
    ) -> StageResult: ...
