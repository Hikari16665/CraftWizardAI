from typing import ClassVar
from pydantic import BaseModel
import yaml


class ModelConfig(BaseModel):
    base_url: str
    api_key: str


class Config(BaseModel):
    """
    配置类 单例
    """

    instance: ClassVar["Config"] = None

    model: ModelConfig

    @classmethod
    def load_config(cls) -> "Config":
        """
        加载配置文件
        """
        if cls.instance is None:
            with open("config.yml", "r") as f:
                config = cls(**yaml.safe_load(f))
            cls.instance = config
        return cls.instance
