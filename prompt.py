import asyncio

from noneprompt import Choice, InputPrompt, ListPrompt

OPTIONS_YN = ["是", "否"]


async def promptSelect(options: list["str"], prompt: str) -> int:
    choices = [Choice(options[i], data=i) for i in range(len(options))]
    prompt_task = asyncio.create_task(
        ListPrompt(
            prompt,
            question_mark="[CraftWizard]",
            pointer=">",
            choices=choices,
            annotation="选择一个选项",
        ).prompt_async()
    )
    select = await asyncio.gather(prompt_task)
    return select[0].data


async def promptInput(prompt: str) -> str:
    prompt_task = asyncio.create_task(
        InputPrompt(prompt, question_mark="[CraftWizard]").prompt_async()
    )
    _input = await asyncio.gather(prompt_task)
    return _input[0]


async def promptConfirm(prompt: str) -> bool:
    # prompt_task = asyncio.create_task(ConfirmPrompt(prompt,default_choice=False).prompt_async())
    # confirm = await asyncio.gather(prompt_task)
    # return confirm[0]
    return bool(await promptSelect(OPTIONS_YN, prompt) == 0)
