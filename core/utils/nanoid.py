from nanoid import generate

def generate_nanoid_32():
    nanoid = generate('_-0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', size=32)
    return nanoid