from dataclasses import dataclass, field


@dataclass
class Block:
    field_idxs: list = field(default_factory=list)
    curr_top_left: list = field(default_factory=lambda: [None, None])
    curr_bottom_right: list = field(default_factory=lambda: [None, None])
    next_top_left: list = field(default_factory=lambda: [None, None])
    next_bottom_right: list = field(default_factory=lambda: [None, None])
    color: tuple = field(default_factory=lambda: [None, None, None])

    def reset(self):
        self.field_idxs = list()
