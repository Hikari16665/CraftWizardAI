from openai import AsyncOpenAI
from pydantic import BaseModel
import pytest
from model import Context
from config import Config
from model.tool_calling import BaseTool
from typing import List, Optional
import json


class OpenAICallResult(BaseModel):
    result: str
    context: Context
    config: Config
    prompt: str
    tools: Optional[List[BaseTool]] = None
    tool_usages: int = 0

    def json_parse_dict(self) -> dict:
        loaded = json.loads(self.result)
        if not isinstance(loaded, dict):
            raise ValueError("OpenAI api调用结果不是json字典")
        return loaded

    def json_parse_list(self) -> list:
        loaded = json.loads(self.result)
        if not isinstance(loaded, list):
            raise ValueError("OpenAI api调用结果不是json列表")
        return loaded

    async def drop(self) -> "OpenAICallResult":
        for _ in range(
            (self.tool_usages) + 1
        ):  # 此处+1是为了确保删除最新的助手回复和所有工具调用
            self.context.drop_latest_context()


async def openai_call(
    context: Context, prompt: str, tools: Optional[List[BaseTool]] = None
) -> OpenAICallResult:
    """调用OpenAI api

    Args:
        context (Context): 原有上下文对象
        prompt (str): 新的用户提示词
        tools (Optional[List[BaseTool]]): 可选的工具列表

    Returns:
        OpenAICallResult: 包含调用结果和更新后的上下文对象
    """
    config = Config.load_config()
    client = AsyncOpenAI(base_url=config.model.base_url, api_key=config.model.api_key)
    context.add_user_context(prompt)
    context_dict = context.get_context_dict()

    # 准备工具参数
    tools_dict = None
    if tools:
        tools_dict = [tool.to_dict() for tool in tools]

    # 首次API调用
    response = await client.chat.completions.create(
        model="qwen3-coder-plus",  # 使用通义千问模型
        messages=context_dict,
        temperature=0.3,
        tools=tools_dict,
        tool_choice="auto" if tools else None,
    )

    tool_usage_context_len = 0

    # 处理工具调用
    message = response.choices[0].message
    if message.tool_calls:
        # 将助手的消息添加到上下文
        context.add_assistant_context(message.content or "")

        for tool_call in message.tool_calls:
            tool_usage_context_len += 1

            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            tool = next((t for t in tools if t.name == function_name), None)
            if tool:
                tool_result = await tool.run(**function_args)

                context_dict = context.get_context_dict()
                context_dict.append(
                    {
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tool_call.id,
                    }
                )
            else:
                # 找不到对应的工具添加错误信息
                context_dict = context.get_context_dict()
                context_dict.append(
                    {
                        "role": "tool",
                        "content": f"Error: Tool {function_name} not found",
                        "tool_call_id": tool_call.id,
                    }
                )

        # 使用工具调用结果进行第二次API调用
        final_response = await client.chat.completions.create(
            model="qwen3-coder-plus",
            messages=context_dict,
            temperature=0.3,
        )
        result = final_response.choices[0].message.content
        tool_usage_context_len += 1
    else:
        # 没有工具调用
        result = message.content

    if result:
        context.add_assistant_context(result)

    return OpenAICallResult(
        result=result or "",
        context=context,
        config=config,
        prompt=prompt,
        tools=tools,
        tool_usages=tool_usage_context_len,
    )


@pytest.mark.asyncio
async def test_openai_call():
    context = Context()
    chat_prompt = "Hello!"
    result = await openai_call(context, chat_prompt)
    assert result.result != ""
    context.reset()
    command_prompt = "directly return a JSON object with the key result and value true, DO NOT use markdown format."
    result = await openai_call(context, command_prompt)
    assert result.result != ""
    assert json.loads(result.result) == {"result": True}
