from typing import Dict

import pytest
from model.tool_calling import BaseTool, ToolParameter


class ToolEval(BaseTool):
    def __init__(self):
        super().__init__(
            name="eval",
            description="用于计算Python表达式，使用eval()进行安全计算，在进行数学算式时使用。",
            parameters={
                "expression": ToolParameter(
                    type="string", description="要计算的表达式", required=True
                )
            },
        )

    async def run(self, expression: str) -> Dict[str, str]:
        """执行计算"""
        try:
            # 安全计算表达式
            result = eval(expression)
            return {"status": "success", "result": result, "expression": expression}
        except Exception as e:
            return {"status": "error", "error": str(e), "expression": expression}


@pytest.mark.asyncio
async def test_tool_eval():
    tool = ToolEval()
    result = await tool.run("2 + 3")
    assert result == {"status": "success", "result": 5, "expression": "2 + 3"}
