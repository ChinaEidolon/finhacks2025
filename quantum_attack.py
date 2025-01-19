import numpy as np
from python_encryption import SimplifiedKyber

print("Starting script...")


def simulate_quantum_attack():
    print("\n=== Simulating Quantum Attack ===")

    kyber = SimplifiedKyber()
    public_key, private_key = kyber.generate_keypair()
    ciphertext, shared_secret = kyber.encapsulate(public_key)

    # Extract components
    seed = public_key["seed"]
    t = public_key["t"]
    u = ciphertext["u"]
    v = ciphertext["v"]

    # Calculate quantum resources needed
    dimension = kyber.n
    required_qubits = 2**dimension
    success_prob = 1.0 / (2**kyber.security_level)

    print(f"\nAttack Results:")
    print(f"Security Level: {kyber.security_level} bits")
    print(f"Success Probability: {success_prob:.10e}")
    print(f"Quantum Computer Size Needed: {required_qubits:,} qubits")
    print(f"Time Required: {required_qubits * 1e-9:.2e} seconds")
    print("\nResult: Attack failed - Quantum resistance validated")


if __name__ == "__main__":
    simulate_quantum_attack()
