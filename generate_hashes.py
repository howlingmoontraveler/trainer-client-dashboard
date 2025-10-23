from werkzeug.security import generate_password_hash

# Generate password hashes for demo accounts
password = 'password123'
hash1 = generate_password_hash(password)
hash2 = generate_password_hash(password)

print("Trainer hash:", hash1)
print("Client hash:", hash2)
