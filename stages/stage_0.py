import logging
from model import openai_call
import prompt
from stages.astage import AStageProcessor, StageResult

logger = logging.getLogger(__name__)


class StageInitProcessor(AStageProcessor):
    """初始化阶段处理器"""

    async def process(self, stage_manager, context, config) -> StageResult:
        """初始化阶段处理"""

        context.add_system_context(
            "你是一个具有多年开发经验的开发助手，"
            "您的任务是根据用户的需求完成需求确认，项目结构确认，插件代码生成等任务。"
            "请全程使用纯文本格式进行回复，禁止使用Markdown格式。"
        )

        user_demand = await prompt.promptInput(
            "请输入您对插件的描述（如需求，功能，使用场景等）："
        )

        demand_call_result = await openai_call.openai_call(
            context,
            f'用户需要一个Minecraft Java版本的Paper服务端插件的代码，需求为：{user_demand}\n请根据需求进一步提问以确保你对需求是明确的，返回格式为：["问题1", "问题2", ...]',
        )

        while True:
            try:
                demand_to_confirm = demand_call_result.json_parse_list()
            except ValueError:
                demand_call_result.drop()
            if demand_to_confirm:
                break

        demand_answers = []
        for question in demand_to_confirm:
            logger.info(f"AI需要进一步了解需求：{question}")
            demand_answers.append(
                await prompt.promptInput("AI需要进一步了解需求，请输入您的回答：")
            )

        demand_qa = str(dict(zip(demand_to_confirm, demand_answers)))

        demand_confirm_result = await openai_call.openai_call(
            context,
            f"已经确认用户需求并细化：{user_demand}\n{demand_qa}，请根据需求向用户复述所有的项目需求，无需添加技术细节，使用纯文本。",
        )
        demand_confirm = demand_confirm_result.result

        logger.info(f"AI已经总结您的需求：{demand_confirm}")

        if not await prompt.promptConfirm("AI的理解是否满足您的需求？"):
            return StageResult(
                success=False,
                context=context,
            )

        context.add_user_context("用户已确认需求。")
        await stage_manager.next_stage()
        return StageResult(
            success=True,
            context=context,
        )
