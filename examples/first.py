from main import StateMan

# create a state manager with static properties as values.
state = StateMan({'foo': 3, 'bar': 5})  # args: dict of properties
# more static properties can be added after initialization.
state.track_static('baz', 6)  # args: name, value
# the whole model is passed to the handler.
state.bind('foo', lambda model, changed: print(f'Foo changed to {model["foo"]}'))  # args: prop, handler
state.bind('bar', lambda model, changed: print(f'Bar changed to {model["bar"]}'))
# pass a tuple to bind to multiple properties
state.bind(('foo', 'bar'), lambda model, changed: print(f'foo + bar = {model["foo"] + model["bar"]}'))  # args: tuple of props, handler
# use `bind_all` bind to all properties (mostly for debugging). The handler is passed three args in this case: the event ('new' or 'changed'), the property that
# changed, and, of course, the model.
state.bind_all(lambda event, model, changed: print(f'Something changed! {changed} is now {model[changed]}'))
