"""Expose an unhandled dataset split during static checking."""

from typing import Literal, TypeAlias, assert_never

Split: TypeAlias = Literal["train", "validation", "test"]


def may_fit_preprocessor(split: Split) -> bool:
    """Allow fitting only on the training split."""
    match split:
        case "train":
            return True
        case "validation" | "test":
            return False
        case _:
            assert_never(split)


allowed = may_fit_preprocessor("train")
# rejected[bad-argument-type]: may_fit_preprocessor("holdout")
