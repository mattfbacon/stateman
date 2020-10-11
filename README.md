# StateMan

<p align='center'><img src='https://raw.githubusercontent.com/mattfbacon/stateman/main/logo.svg' alt='Logo'></p>

A tiny explicit state manager. No dependencies and only 89 SLOCs (3156 bytes minified) according to Al Danial's `cloc` utility.

The purpose of StateMan is to manage state with explicit bindings for changes. In other similar state frameworks, the dependencies are automatically detected. The goal of StateMan is to avoid unexpected updates based on dependency detection that thinks too highly of itself. StateMan requires the user to provide the dependencies explicitly, so every update is expected.

StateMan does not track or detect external changes to properties. If you want a change that is not tracked to cause an update, it is most likely due to the following situation:

You are externally changing properties of an object that was passed by reference to StateMan. Consider acting on the object within the StateMan instance. Note that calling methods on the object will not cause an update even if you are acting on StateMan's reference. You may need to rethink your situation, as generally an object with methods should not be part of the state.

However, for a simple way to manually cause an update, see `_handle_change`. This is by no means discouraged and may well be necessary in a complex situation, since StateMan is quite simple with respect to how it decides when to update.

Vocabulary:

- to Track: to store a value and possibly fulfill actions when the value is changed.

- to Depend on: to require an update when the dependency is updated.

- Property: a key and value that are tracked by StateMan.

- Static Property: a property that will only change if the user changes it.

- Dynamic Property: a property that is defined in terms of other properties. Dependencies are specified so StateMan knows when the property would update.

- Binding: a directive to StateMan to call the provided handler when the property it is bound to changes, whether as a result of being changed explicitly, or as a dynamic property being updated due to one of its dependencies updating. Similar to a "watcher" in other state management frameworks.

- Model: in the Model–View–Controller pattern, the model is "the application's dynamic data structure, independent of the user interface." (from Wikipedia)

At the moment there is no way to "delete" a property, binding, or dependency, simply because the need has not come up for me and so it's not worth it to needlessly expand the code. However, I may decide to implement it later, or if you submit a PR implementing it I will most likely merge it.

## Documentation and Usage

The documentation is in the form of docstrings in `stateman.py`.

To use StateMan in a project, copy `stateman.min.py` to your project directory. I suggest renaming it to `stateman.py`.    
Note that StateMan can only be used without express permission in open-source projects. If you want to use it in closed-source/proprietary software,

## License

Copyright (C) 2020  Matt Fellenz [mattf53190@gmail.com](mailto:mattf53190@gmail.com)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.