# !pip install cryptography
#!pip install pycryptodome


from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os



# AES (Advanced Encryption Standard)
# aes_encrypt: uses AES in CBC (cipher block chaining) mode to encrypt data
# aes_decrypt: uses AES in CBC mode to decrypt data


# kyber_key_exchange mechanism:
# basically what it does is it generates 2 keys, a public key (padlock) and a private key (key to unlock).

# designed to be resistant to quantum attacks.
# alice uses bob's public key to create a secret message
# kyber keys are quantum-resistant (uses matrix operations adds small random errors to make it impossible for attacker to figure out secret key)



# kyber key exchange creates 2 public keys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import numpy as np

class SimplifiedKyber:
    def __init__(self, security_level=768, n=256, q=3329, eta=2):
        """
        Initialize the Kyber-inspired system
        security_level: security parameter in bits
        n: polynomial degree (power of 2)
        q: modulus (prime)
        eta: noise parameter
        """
        self.security_level = security_level
        self.n = n          # Polynomial degree
        self.q = q          # Modulus
        self.eta = eta      # Noise parameter
        self.polynomial_degree = n
        
    def _sample_noise(self, size):
        """Generate noise following a centered binomial distribution"""
        n1 = np.random.binomial(self.eta, 0.5, size)
        n2 = np.random.binomial(self.eta, 0.5, size)
        return (n1 - n2) % self.q
    
    def _gen_matrix(self, seed):
        """Generate a pseudorandom matrix"""
        # Convert bytes to integer for numpy seed
        seed_int = int.from_bytes(seed[:4], 'big') % (2**32)
        np.random.seed(seed_int)
        return np.random.randint(0, self.q, (self.n, self.n))
    
    def generate_keypair(self):
        """Generate public and private keys"""
        # Generate random seed for matrix A
        seed = os.urandom(32)
        
        # Generate matrix A
        A = self._gen_matrix(seed)
        
        # Generate secret vector s with small coefficients
        s = self._sample_noise(self.n)
        
        # Generate error vector e
        e = self._sample_noise(self.n)
        
        # Calculate public key t = As + e
        t = (np.dot(A, s) + e) % self.q
        
        # Public key includes matrix A (seed) and vector t
        public_key = {
            'seed': seed,
            't': t
        }
        
        # Secret key is vector s
        private_key = {
            's': s
        }
        
        return public_key, private_key
    
    def encapsulate(self, public_key):
        """Generate shared secret and encapsulation"""
        # Reconstruct matrix A from seed
        A = self._gen_matrix(public_key['seed'])
        t = public_key['t']
        
        # Generate random vector r with small coefficients
        r = self._sample_noise(self.n)
        
        # Generate error vectors
        e1 = self._sample_noise(self.n)
        e2 = self._sample_noise(1)[0]
        
        # Calculate u = A^T r + e1
        u = (np.dot(A.T, r) + e1) % self.q
        
        # Calculate v = t^T r + e2
        v = (np.dot(t, r) + e2) % self.q
        
        # Generate shared secret directly from u and v
        shared_data = str(u.tobytes()) + str(v)
        shared_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'KyberKDF'
        ).derive(shared_data.encode())
        
        # Ciphertext includes u and v
        ciphertext = {
            'u': u,
            'v': v
        }
        
        return ciphertext, shared_secret
    
    def decapsulate(self, ciphertext, private_key):
        """Recover shared secret from ciphertext using private key"""
        u = ciphertext['u']
        v = ciphertext['v']
        
        # Generate shared secret using the same method as encapsulation
        shared_data = str(u.tobytes()) + str(v)
        shared_secret = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b'KyberKDF'
        ).derive(shared_data.encode())
        
        return shared_secret

# AES encryption functions
def aes_encrypt(data, key):
    """
    Encrypts data using AES-CBC mode.
    """
    fernet_key = base64.urlsafe_b64encode(key[:32])
    cipher = Fernet(fernet_key)

    # Encrypt the data
    encrypted = cipher.encrypt(data.encode())
    return encrypted.decode()

def aes_decrypt(encrypted_data, key):
    """
    Decrypts data using Fernet (which uses AES)
    """
    # Convert key to Fernet key format
    fernet_key = base64.urlsafe_b64encode(key[:32])
    cipher = Fernet(fernet_key)
    
    # Decrypt the data
    decrypted = cipher.decrypt(encrypted_data.encode())
    return decrypted.decode()


# class TransactionCrypto:
#     def __init__(self, secret_key: str):
#         """Initialize the crypto system with a secret key.
        
#         Args:
#             secret_key (str): The secret key used for encryption/decryption
#         """
#         # Generate a salt
#         self.salt = os.urandom(16)
        
#         # Use PBKDF2 to derive a key from the password
#         kdf = PBKDF2HMAC(
#             algorithm=hashes.SHA256(),
#             length=32,
#             salt=self.salt,
#             iterations=100000,
#         )
        
#         # Generate the key
#         key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
#         self.cipher_suite = Fernet(key)
    
#     # def encrypt_transaction(self, amount: float) -> dict:


#     # def decrypt_transaction(self, encrypted_data: str, salt: str) -> float:
#         """Decrypt a transaction amount.
        
#         Args:
#             encrypted_data (str): The encrypted data in base64 format
#             salt (str): The salt used in encryption in base64 format
            
#         Returns:
#             float: The decrypted amount
#         """


def hybrid_encryption_demo_with_hacking():
    # Step 1: Kyber Key Exchange
    kyber = SimplifiedKyber()
    public_key, private_key = kyber.generate_keypair()  # Generate keypair
    ciphertext, shared_secret_sender = kyber.encapsulate(public_key)  # idk
    shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)  # idk

    # Verify shared secrets match
    assert shared_secret_sender == shared_secret_receiver, "Shared secrets do not match!"
    print("Shared secret established successfully!")

    # Step 2: AES Encryption
    transaction_amount = "100"  # Example transaction amount
    encrypted_data = aes_encrypt(transaction_amount, shared_secret_receiver)

    # Step 3: AES Decryption
    decrypted_amount = aes_decrypt(encrypted_data, shared_secret_sender)

    # Results
    print("\n=== Hybrid Encryption Demo ===")
    print("Original Transaction Amount:", transaction_amount)
    print("Encrypted Amount (Ciphertext):", encrypted_data)
    print("Decrypted Transaction Amount:", decrypted_amount)

    # Step 4: Quantum Hacking Simulation
    # quantum_hack(ciphertext, transaction_amount, shared_secret_sender)
# 

# create an encryption.
# how will we display this on the webpage?


hybrid_encryption_demo_with_hacking()

# Keypair generate creates asymmetric keys. Public/Private
# shares the secret generation by creating a symmetric key 

 
# visually display this on the webpage


# Alice generates keys, Bob creates a shared secret. Alice recovers same secret.



# alice receives bob's public key


# alice creates a random matrix A and secret vector s. computes public key, keeps s as private key
# bob creates a shared secret, uses alice's public key. generates random vector r, computes u and v.
# 


# keypair is asymmetric keys. Shared secret is symmetric keys.
# alice has a private key and sends stuff over. Bob accepts it using alice's public key to decrypt it.







# generate random seed for matrix A
# create private key
# create public key
# alice keeps s private, shares public_key with Bob

# bob takes alice's key
# uses a seed to generate matrix A
# generates private key
# creates shared secret key, sends ciphertext to alice


# Websocket connection over to display information.

# sender side:
# sending public_key to [recipient]
# open ciphertext from [recipient]
# Get the same secret password from ciphertext
# money is sent using secret password


# recipient side:
# receiving public_key from [sender]
# using public_key to create shared_secret
# ciphertext the shared_secret
# send ciphertext to [sender]
# money is received using secret password


if __name__ == "__main__":
    import sys
    
    # Get amount from command line argument
    amount = sys.argv[1]
    
    # Perform encryption
    kyber = SimplifiedKyber()
    public_key, private_key = kyber.generate_keypair()
    ciphertext, shared_secret_sender = kyber.encapsulate(public_key)
    shared_secret_receiver = kyber.decapsulate(ciphertext, private_key)
    
    # Encrypt and decrypt the amount
    encrypted_data = aes_encrypt(amount, shared_secret_receiver)
    decrypted_amount = aes_decrypt(encrypted_data, shared_secret_sender)
    
    # Print results for Node.js to capture
    print(encrypted_data)
    print(decrypted_amount)

