import flet
from flet import Icons
print('Icons attr exists? ', hasattr(Icons, 'FUEL'))
print('Icons FUEL value: ', getattr(Icons, 'FUEL', None))
print('Icons names starting FUEL: ', [n for n in dir(Icons) if n.startswith('FUEL')])
