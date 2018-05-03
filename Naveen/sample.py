import sys
import os

sys.path.insert(0, os.path.join('.', 'Backup'))
from Hello import Hello

hel = Hello(45)
hel.print_val()

print os.path.abspath('.')
print os.path.relpath(os.path.abspath('.'))