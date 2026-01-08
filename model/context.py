from abc import ABC

from pydantic import BaseModel


class Context(BaseModel):
    class AContext(ABC, BaseModel):
        """
        上下文基类
        """

        pass

    class ContextAssistant(AContext, BaseModel):
        """
        助手上下文
        """

        assistant_prompt: str

    class ContextSystem(AContext, BaseModel):
        """
        系统上下文
        """

        system_prompt: str

    class ContextUser(AContext, BaseModel):
        """
        用户上下文
        """

        user_prompt: str

    context: list[AContext] = []

    def _add_context(self, context: AContext) -> None:
        self.context.append(context)

    def add_assistant_context(self, assistant_prompt: str) -> None:
        """
        添加助手上下文
        """
        self._add_context(self.ContextAssistant(assistant_prompt=assistant_prompt))

    def add_user_context(self, user_prompt: str) -> None:
        """
        添加用户上下文
        """
        self._add_context(self.ContextUser(user_prompt=user_prompt))

    def add_system_context(self, system_prompt: str) -> None:
        """
        添加系统上下文
        """
        self._add_context(self.ContextSystem(system_prompt=system_prompt))

    def drop_latest_context(self) -> None:
        """
        删除最新上下文
        """
        if self.context:
            self.context.pop()

    def get_context_dict(self) -> dict:
        """
        生成上下文字典
        """
        context_dict = []
        for ctx in self.context:
            if isinstance(ctx, self.ContextAssistant):
                context_dict.append(
                    {"role": "assistant", "content": ctx.assistant_prompt}
                )
            elif isinstance(ctx, self.ContextUser):
                context_dict.append({"role": "user", "content": ctx.user_prompt})
        return context_dict

    def reset(self) -> None:
        """
        重置上下文
        """
        self.context = []
