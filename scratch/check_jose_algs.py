from jose import jwt
from jose.backends import _backends

print("Backends cargados en jose:")
for name, backend in _backends.items():
    print(f" - {name}: {backend}")

# Intentar decodificar un token con algoritmo RS256 simulado para ver si levanta error
print("\nSoporte de algoritmos en jose:")
try:
    # Ver si soporta RS256
    jwt.jws.verify('eyJhbGciOiJSUzI1NiJ9.eyJnIjoiYiJ9.c2ln', 'key', algorithms=['RS256'])
except Exception as e:
    print(f"Error al verificar RS256: {e}")
