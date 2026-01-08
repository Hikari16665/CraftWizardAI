from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数定义"""

    type: str
    description: str
    required: bool = True


class BaseTool(ABC, BaseModel):
    """工具基类"""

    name: str
    description: str
    parameters: Dict[str, ToolParameter]

    @abstractmethod
    async def run(self, **kwargs) -> Any:
        """执行工具的抽象方法"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """将工具转换为字典格式，用于API调用"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        param_name: {
                            "type": param.type,
                            "description": param.description,
                        }
                        for param_name, param in self.parameters.items()
                    },
                    "required": [
                        param_name
                        for param_name, param in self.parameters.items()
                        if param.required
                    ],
                },
            },
        }
