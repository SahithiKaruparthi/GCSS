
from werkzeug.security import generate_password_hash

# Example: Hash 'password123'
hashed_password = generate_password_hash('password123')
print(hashed_password)