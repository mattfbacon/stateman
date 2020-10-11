'''StateMan: A tiny explicit state manager. No dependencies and only 92 SLOCs (3157 bytes minified) according to Al Danial's `cloc` utility.

Copyright (C) 2020  Matt Fellenz

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

---

The purpose of StateMan is to manage state with explicit bindings for changes. In other similar state frameworks, the dependencies are automatically
detected. The goal of StateMan is to avoid unexpected updates based on dependency detection that thinks too highly of itself. StateMan requires the
user to provide the dependencies explicitly, so every update is expected.

StateMan does not track or detect external changes to properties. If you want a change that is not tracked to cause an update, it is most likely due to
the following situation:

You are externally changing properties of an object that was passed by reference to StateMan. Consider acting on the object within the StateMan instance.
Note that calling methods on the object will not cause an update even if you are acting on StateMan's reference. You may need to rethink your situation,
as generally an object with methods should not be part of the state.

However, for a simple way to manually cause an update, see ``_handle_change``. This is by no means discouraged and may well be necessary in a complex
situation, since StateMan is quite simple with respect to how it decides when to update.

Vocabulary:
- to Track: to store a value and possibly fulfill actions when the value is changed.
- to Depend on: to require an update when the dependency is updated.
- Property: a key and value that are tracked by StateMan.
- Static Property: a property that will only change if the user changes it.
- Dynamic Property: a property that is defined in terms of other properties. Dependencies are specified so StateMan knows when the property would update.
- Binding: a directive to StateMan to call the provided handler when the property it is bound to changes, whether as a result of being changed explicitly,\
or as a dynamic property being updated due to one of its dependencies updating. Similar to a "watcher" in other state management frameworks.
- Model: in the Model–View–Controller pattern, the model is "the application's dynamic data structure, independent of the user interface." (from Wikipedia)

At the moment there is no way to "delete" a property, binding, or dependency, simply because the need has not come up for me and so it's not worth it to
needlessly expand the code. However, I may decide to implement it later, or if you submit a PR implementing it I will most likely merge it.'''

from itertools import chain
from typing import Callable, List, Tuple, Union, Optional
from functools import reduce


class StateMan:
	__slots__ = ['bindings', 'global_bindings', 'dependencies', 'dependents', 'static_props', 'dynamic_props', 'refs', 'cache', 'nocache']

	def __init__(self, props: dict, literal: bool=False, refs: Optional[dict]=None):
		'''Create a new StateMan instance.\n
		Arguments: `props` (dict) | Keyword Arguments: `literal` (bool, default False), `refs` (dict, default {})

		Static and dynamic properties can be defined in the `props` dictionary.
		The keys of the dictionary can be any type that can be used as a dictionary key, not just strings.
		For static properties, simply provide the value.
		For dynamic properties, for the value provide a tuple (or list) of the format `(getter, dependencies, setter?, cache?)`.
		`getter` is a function that takes the StateMan instance as its single argument.
		`dependencies` is a tuple (or list) of the properties (static or dynamic) that should, upon change, cause this property to be updated.
		`setter` is an optional function that takes the StateMan instance and the provided value as arguments. If a setter is not included then the property will
		not have a setter and will raise a `TypeError` upon attempts to set it.
		`cache` is an optional boolean for whether the property should be cached.
		For more detail about these options see the docstring for ``track_dynamic``.

		`literal` forces all entries in the dictionary to be treated as static properties, even if they look like a dynamic property.

		`refs` is included specifically for when certain objects need to be accessed by the handlers, like a window object for a GUI app.
		These could theoretically be stored in static properties, but for large objects that don't need to be tracked, moving them to `refs` may lead to
		slight performance improvements in some circumstances. However, the main reason you would do this is to prevent it from being bound, which would
		impact the performance.'''
		self.bindings = {}
		self.global_bindings = []
		self.dependents = {}
		self.static_props = {}
		self.dynamic_props = {}
		self.cache = {}
		self.nocache = []
		self.refs = refs if refs is not None else {}

		if literal:
			self.static_props = props
			self.dependents = {k: [] for (k, v) in props}
		else:
			for prop in props:
				value = props[prop]
				if StateMan._is_dynamic_prop_definition(value): self.track_dynamic(prop, *value)
				else: self.track_static(prop, value)

	def bind(self, prop_or_props: Union[any, List[any], Tuple[any]], handler: Callable[[dict, any], None]):
		'''Create a binding to a property or properties.\n
		Arguments: `prop_or_props` (property name or list/tuple of property names), `handler` (function taking the model and the name of the changed property)

		If you are binding to a single property, give the name of that property (whether it be a string, number, or anything else that can be used as a
		dictionary key) for the `prop_or_props` argument.
		If you are binding to multiple properties, give a list or tuple of the property names.

		The handler takes two arguments: the model, which is just the StateMan instance, and the name of the property that changed. While for bindings to a single
		property it may seem redundant to provide the name of the changed property, it is important for bindings to multiple properties. Thus, for consistency's
		sake, it is provided for all handlers.'''
		if isinstance(prop_or_props, (list, tuple)):
			for prop in prop_or_props: self.bind(prop, handler)
		else:
			if prop_or_props in self.static_props or prop_or_props in self.dynamic_props:
				if prop_or_props not in self.bindings: self.bindings[prop_or_props] = [handler]
				else: self.bindings[prop_or_props].append(handler)
			else: self.__missing__(prop_or_props)

	def bind_all(self, handler: Callable[[str, dict, any], None]):
		'''Bind to any change.
		Arguments: `handler` (function taking the type of event ['new' or 'changed'], the model, and the name of the changed or newly created property)

		This is useful for debugging.'''
		self.global_bindings.append(handler)

	def track_static(self, prop, value):
		'''Track a static property.
		Arguments: `prop` (the name of the property), `value` (the value of the property)'''
		if prop not in self.dependents: self.dependents[prop] = []
		self.static_props[prop] = value
		for handler in self.global_bindings: handler('new', self, prop)

	def track_dynamic(self, prop, getter: Callable[[dict], any], dependencies: Union[List[any], Tuple[any]], setter: Optional[Callable[[dict, any], None]]=None, cache: bool=True):
		'''Track a dynamic property with a getter and optional setter\n
		Arguments: `prop` (the name of the property), `getter` (a function taking the model and returning the property's value), `dependencies` (a tuple or list of
		the properties that this property "depends" on (i.e., which properties cause this property to update when they're updated) | Keyword Arguments: `cache`
		(whether the value for this property should be cached)

		Dynamic properties are arguably the most important StateMan feature. You may know them as "getters" or "computed properties" from other state management
		frameworks. However, as with everything else, dynamic properties in StateMan are explicit with respect to their dependencies. You provide them as you would
		with a binding, and StateMan will mark the property as updated (calling the bindings and updating any of its dependencies) when any of the properties in
		the list are updated.

		If you would like to provide a setter, specify it in the `setter` argument. The function takes the model and the provided value as arguments, and need not
		return anything. Since a dynamic property cannot be set directly, the purpose of a dynamic property's setter is to change the values of other static prop-
		erties or otherwise modify the state.

		In some cases, for example if the value of a dynamic property depends on external variables but you don't want to or can't include those variable in the
		state, you may not want the value of the dynamic property to be cached. In this case provide `False` to the keyword argument `cache`. By default dynamic
		properties are cached.'''
		if prop not in self.dependents: self.dependents[prop] = []
		self.dynamic_props[prop] = (getter, setter)
		for dependency in dependencies:
			if dependency not in self.dependents: self.dependents[dependency] = [prop]
			else: self.dependents[dependency].append(prop)
		if not cache: self.nocache.append(prop)
		for handler in self.global_bindings: handler('new', self, prop)

	def __len__(self):
		return len(self.static_props) + len(self.dynamic_props)

	def __iter__(self):
		return chain(self.static_props, self.dynamic_props)

	def __reversed__(self):
		return chain(reversed(self.dynamic_props), reversed(self.static_props))

	def __missing__(self, item):
		raise KeyError(f'Property {item} not found')

	def __contains__(self, item):
		return item in self.static_props or item in self.dynamic_props

	def __getitem__(self, item):
		if item in self.static_props: return self.static_props[item]
		elif item in self.dynamic_props:
			if item in self.nocache:
				return self.dynamic_props[item][0](self)
			else:
				if item not in self.cache: self.cache[item] = self.dynamic_props[item][0](self)
				return self.cache[item]
		else: self.__missing__(item)

	def _walk_deps(self, item):
		'''Internal method to generate a list of all the dependencies for a property with a recursive search.\n
		Arguments: `item` (the name of the property)

		This method does not prune the list for duplicates, but if they are pruned (with `list(dict.fromkeys(result))` to preserve order), they will be in the
		proper order so that if the properties are updated according to the list order, any property will have had all of its dependencies updated by the time
		it is reached.'''
		return reduce(lambda a, b: a + b, [self._walk_deps(dependent) for dependent in self.dependents[item]], [item])

	def _handle_change(self, item):
		'''Internal method to trigger bindings for a property and all its dependencies. May be used externally to force an update.\n
		Arguments: `item` (the name of the property)

		While the main use of this method is internal, it may be used externally to force updates, as mentioned in the class docstring. Simply call the method with
		the name of the property to be updated.'''
		deps = list(dict.fromkeys(self._walk_deps(item)))
		for prop in deps:
			if prop in self.dynamic_props and prop not in self.nocache and prop in self.cache: self.cache.pop(prop)
		for prop in deps:
			for handler in self.global_bindings: handler('changed', self, prop)
			if prop in self.bindings:
				for handler in self.bindings[item]: handler(self, prop)

	def __setitem__(self, item, value):
		if item in self.dynamic_props:
			if self.dynamic_props[item][1] is not None: self.dynamic_props[item][1](self, value)
			else: raise TypeError(f'No setter for dynamic property {item}')
		elif item in self.static_props:
			self.static_props[item] = value
			self._handle_change(item)
		else:
			self.track_static(item, value)
			for handler in self.global_bindings: handler('new', self, item)

	@staticmethod
	def _is_dynamic_prop_definition(definition):
		'''Internal method to check if a value is a dynamic property definition.\n
		Arguments: `definition` (the value to check)

		A dynamic property definition is of the form `[getter: function, dependencies: list or tuple, setter?: function]`, where the outermost array can be a list
		or tuple.'''
		if isinstance(definition, (list, tuple)):
			length = len(definition)
			return (length == 2 or (length == 3 and callable(definition[2]) and ((not length == 4) or isinstance(definition[3], bool)))) and callable(definition[0]) and isinstance(definition[1], (list, tuple))
		else: return False
