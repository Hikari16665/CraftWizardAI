import logging
from typing import Any, Dict
from bs4 import BeautifulSoup
import pytest
from model.tool_calling import BaseTool, ToolParameter

import httpx

PAPER_JD_URL = "https://jd.papermc.io/paper/1.21.11/"


logger = logging.getLogger(__name__)


class ToolQueryPaperAPI(BaseTool):
    def __init__(self):
        super().__init__(
            name="query_paper_api",
            description="查询Paper API用法，包括方法，方法参数、返回值等，请严格按照API进行编写，善用查询",
            parameters={
                "package_name": ToolParameter(
                    type="string",
                    description="要查询的包名称，例如: org.bukkit.entity",
                    required=True,
                ),
                "class_name": ToolParameter(
                    type="string",
                    description="要查询的类名称，例如: Player，若不填写则查询包信息，仅可查询类内方法，无法获取继承方法，实现等信息，若要查询继承方法，请直接查询父类或接口",
                    required=False,
                ),
                "method_name": ToolParameter(
                    type="string",
                    description="要查询的方法名称，例如: getLocation()，若有参数请写完整参数，例如broadcastSlotBreak(org.bukkit.inventory.EquipmentSlot)",
                    required=False,
                ),
            },
        )

    async def run(
        self, package_name: str, class_name: str = None, method_name: str = None
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            url = f"{PAPER_JD_URL}{package_name.replace('.', '/')}"
            if class_name:
                url += f"/{class_name}.html"
            else:
                url += "/package-summary.html"
            response = await client.get(url)
            try:
                response.raise_for_status()
                response_text = response.text
            except httpx.HTTPStatusError:
                return {
                    "status": "error",
                    "error": f"查询{package_name}失败: {response.status_code}",
                }
        soup = BeautifulSoup(response_text, "html.parser")
        text = soup.get_text(strip=True, separator=" ")
        if method_name and class_name:
            # find a section element that id is method_name
            method_section = soup.find("section", attrs={"id": method_name})
            if method_section:
                text = method_section.get_text(strip=True, separator=" ")
        logger.info(f"查询{package_name}成功: {text[:50]} ... ({len(text)} chars)")

        return {"status": "success", "result": text}


@pytest.mark.asyncio
async def test_tool_query_paper_api():
    tool = ToolQueryPaperAPI()
    e_entity = await tool.run("org.bukkit.entity")
    assert "org.bukkit.entity" in e_entity["result"]
    e_fail = await tool.run("org.bukkit.that.does.not.exist")
    assert e_fail["status"] == "error"
    e_player = await tool.run("org.bukkit.entity", "Player")
    assert "extends HumanEntity" in e_player["result"]
    e_method = await tool.run("org.bukkit.entity", "Entity", "getLocation()")
    assert "Gets the entity's current position" in e_method["result"]
