# Exhaustive matching

[Project overview and reading path](../README.md)

A data pipeline decides which splits may fit a preprocessor. Later, someone adds a `holdout` split. Existing decisions should be reviewed when the set changes.

**Typical Python**

```python,ignore
def may_fit_preprocessor(split: str) -> bool:
    match split:
        case "train":
            return True
        case _:
            return False


allowed = may_fit_preprocessor("holdout")
```

The new split silently falls into the default. Nothing tells the author that an existing decision now covers an unreviewed case.

**Alternative**

```python,ignore
Split = Literal["train", "validation", "test"]


def may_fit_preprocessor(split: Split) -> bool:
    match split:
        case "train":
            return True
        case "validation" | "test":
            return False
        case _:
            assert_never(split)


allowed = may_fit_preprocessor("train")
```

[Source](../examples/exhaustive_matching.py)

The function returns `True` for `"train"` and `False` for the other declared
splits. Adding `"holdout"` to `Split` without updating the match produces a checker
error at `assert_never`: a possible value remains unhandled.

This checks completeness of the decision, not data provenance. A dataset named
`"train"` can still contain the wrong records. Unchecked input reaching
`assert_never` also fails at runtime.
