# Numeric annotations and runtime patterns

[Project overview and reading path](../README.md)

A formatter accepts a floating-point score. Callers may also supply an integer such as zero, which Python typing permits for a float parameter.

**Typical Python**

```text
match score:
    case float(value):
        return f"{value:.3f}"
```

The annotation accepts `0`, but the runtime `float` pattern does not match an integer. A type-correct call can miss the handler.

**Alternative**

```text
match score:
    case int(value) | float(value):
        return f"{value:.3f}"
```

Both `0` and `0.0` produce `"0.000"`. This repairs runtime behavior; it does not
add a static guarantee. For an undefined score, [return a typed outcome](absence.md)
and match that outcome before formatting.
