# Plugin discovery at the boundary

[Project overview and reading path](../README.md)

An application discovers a third-party plugin at startup. Discovery gives it an object, not evidence that the object honors its application interface.

**Typical Python**

```python,ignore
plugin = entry_point.load()
prediction = plugin(request)
```

Loading discovers a callable but leaves its accepted request and returned value
implicit. A wrong interface is discovered only when the plugin is called.

**Alternative**

```python,ignore
vendor_call = entry_point.load()
predictor = bind_vendor(vendor_call)
```

The [SDK adapter](third-party-boundaries.md) exposes a checked `Predictor` to the
application. It validates call results and represents ordinary call failures as
outcomes. The checker can then reject incorrect request types and unchecked
success access.

Loading, configuration, and construction belong at startup. Runtime validation
is still necessary, and this adapter does not sandbox plugin code.
`@runtime_checkable` cannot prove method signatures or behavior.
