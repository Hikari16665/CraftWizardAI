from enum import Enum


class PluginStage(Enum):
    INIT = 0
    DEP_DECLAIR = 1
    META_FILL = 2
    CODE_STRUCT = 3
    CODE_FILL = 4
    COMPILE = 5
    PACKAGE = 6
    COMPLETE = 7
