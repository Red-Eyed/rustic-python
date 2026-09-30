# Prefer total operations for expected failures

[Project overview and reading path](../README.md)

A user lookup may receive an ID that is absent from the current mapping. The
caller can report the missing ID and continue, so absence is part of the valid
input domain. An operation that has a defined outcome for every valid input is
*total*; an operation that can fail for a valid input is *partial*.

**Typical Python**

```python,ignore
def find_user(users: Mapping[str, User], user_id: str) -> User:
    return users[user_id]


user = find_user(users, "u-9")
```

If `users` contains only `"u-7"`, this call raises `KeyError` at runtime. Its
return annotation does not tell the caller that a missing ID needs handling.

**Alternative**

```python,ignore
def find_user(users: Mapping[str, User], user_id: str) -> Result[User, UserNotFound]:
    user = users.get(user_id)
    if user is None:
        return Err(UserNotFound(user_id))
    return Ok(user)
```

[Source](../examples/total_lookup.py)

`find_user(users, "u-7")` returns `Ok(User(name="Ada"))`;
`find_user(users, "u-9")` returns `Err(UserNotFound(user_id="u-9"))`.
Matching the result produces `"Ada"` or `"user u-9 not found"`. The checker
rejects `found.value.name` before the caller narrows `Ok | Err`, because `Err`
has no `value` attribute. That is the static improvement: the expected missing
key is visible in the return type. The checker does not reject every use of
`users[user_id]` or prove that arbitrary code cannot raise.

Use the same question for `items[index]`, `next(iterator)`, `min(items)`, and
division: can an out-of-range index, exhausted iterator, empty collection, or
zero denominator occur during normal use? If so, choose an explicit outcome
that lets the caller make its real decision. Prefer the small `Result` union
for expected failures the caller can handle; do not build a generic wrapper
around every built-in.
When failure means a broken internal invariant and there is no supported
recovery, let the operation raise. See [Result and match](errors-and-absence.md)
for that distinction.
