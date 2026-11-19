import os
from pwdlib import PasswordHash

# Identifiants strictement réservés aux bases temporaires des tests.
os.environ['AUTH_USERNAME'] = 'test-user'
os.environ['AUTH_PASSWORD_HASH'] = PasswordHash.recommended().hash('Test-password-123456')
os.environ['JWT_SECRET_KEY'] = 'test-only-secret-never-use-in-production-123456'
