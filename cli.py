import asyncio
from config import Config
from managers import StageManager
from model.context import Context
from stages.stage_0 import StageInitProcessor
from structures import PluginStage


def run() -> None:
    asyncio.run(main=_loop())


async def _loop() -> None:
    stage_manager = StageManager()
    context = Context()
    config = Config.load_config()
    await stage_manager.reset_stage()

    while True:
        await _handle_loop(stage_manager, context, config)


async def _handle_loop(
    stage_manager: StageManager, context: Context, config: Config
) -> None:
    """
    处理循环
    """
    match await stage_manager.get_stage():
        case PluginStage.INIT:
            await StageInitProcessor().process(stage_manager, context, config)
