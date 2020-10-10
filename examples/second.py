from main import StateMan

a = StateMan({'x': 1, 'y': 2, 'z': (lambda model: 1, ('x',), lambda model, value: print('test'))})
a.bind_all(lambda event, model, changed: print(f'{changed} changed to {model[changed]}'))
a.track_dynamic('sum', lambda model: model['x'] + model['y'], ('x', 'y'))
a.track_dynamic('sum2', lambda model: model['x'] + model['sum'], ('x', 'sum'))
a.track_dynamic('sum3', lambda model: model['x'] + model['sum2'], ('x', 'sum2'))
