# Encryption of data at rest

**Encryption of data at rest**

<mark style="color:orange;">**Envelope Encryption approach**</mark>

openg2p-registry will generate a cleartext-DEK (Data Encryption Key) at startup

openg2p-registry will sign this DEK using PKI (Mosip Keymanager) - Asymmetric

This ciphertext-DEK will be persisted in the K8S Secrets

During Startup, registry will call KMS and get the cleartext-DEK and keep this in Memory

Some columns (the implementation model will decide which columns to encrypt) will be encrypted

DB Column encryption will be Symmetric Encryption using AES

So DB encryption/decryption will not have latency associated with KMS services

<mark style="color:blue;">**Should I use NONCE resistance?? Possibly overkill?? There is AES-GCM. You will have to store the NONCE value along with the ciphertext (each column/value will have a different NONCE)**</mark>

***

**AES without GCM**

`import os`

`from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes`

`from cryptography.hazmat.primitives import padding`

**`class AESCipher:`**

&#x20;   `BLOCK_SIZE = 128  # AES block size in bits`

**`@staticmethod`**

**`def encrypt(plaintext: str, key: bytes) -> bytes:`**

&#x20;          `# Convert plaintext to bytes`

&#x20;    `plaintext_bytes = plaintext.encode("utf-8")`

&#x20;       `# PKCS7 pad`

`padder = padding.PKCS7(AESCipher.BLOCK_SIZE).padder()`

`padded_data = padder.update(plaintext_bytes) + padder.finalize()`

&#x20;       `# Generate a random 16-byte IV`

&#x20;       `iv = os.urandom(16)`

&#x20;       `cipher = Cipher(`

&#x20;           `algorithms.AES(key),`

&#x20;           `modes.CBC(iv)`

&#x20;       `)`

&#x20;       `encryptor = cipher.encryptor()`

`ciphertext = encryptor.update(padded_data) + encryptor.finalize()`

&#x20;       `# You must store IV + ciphertext together`

&#x20;       `return iv + ciphertext`



**`@staticmethod`**

**`def decrypt(blob: bytes, key: bytes) -> str:`**

&#x20;       `iv = blob[:16]`

&#x20;       `ciphertext = blob[16:]`

&#x20;       `cipher = Cipher(`

&#x20;           `algorithms.AES(key),`

&#x20;           `modes.CBC(iv)`

&#x20;       `)`

&#x20;       `decryptor = cipher.decryptor()`

`padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()`

&#x20;       `# Unpad the plaintext`

`unpadder = padding.PKCS7(AESCipher.BLOCK_SIZE).unpadder()`

`plaintext_bytes = unpadder.update(padded_plaintext) + unpadder.finalize()`

&#x20;       `return plaintext_bytes.decode("utf-8")`

***

`from sqlalchemy import Column, Integer, LargeBinary`

`from sqlalchemy.orm import declarative_base`

`from sqlalchemy.ext.hybrid import hybrid_property`

`from crypto import AESCipher, PLAINTEXT_DEK`

`Base = declarative_base()`

**`class G2PRegister(Base):`**

&#x20;   `__abstract__ = True`

&#x20;   `_register_mnemonic_ = None`

**`def encrypt_value(self, value: str) -> bytes:`**

&#x20;       `if not value:`

&#x20;           `return None`

&#x20; `return AESCipher.encrypt(value, PLAINTEXT_DEK)`

**`def decrypt_value(self, blob: bytes) -> str:`**

&#x20;       `if not blob:`

&#x20;           `return None`

&#x20;  `return AESCipher.decrypt(blob, PLAINTEXT_DEK)`

***

`from sqlalchemy import Column, Integer, LargeBinary`

`from sqlalchemy.orm import declarative_base`

`from sqlalchemy.ext.hybrid import hybrid_property`

`from crypto import AESCipher, PLAINTEXT_DEK`

`Base = declarative_base()`

**`class FarmerRegister(G2PRegister):`**

&#x20;   `_register_mnenomic_ = "farmer"`

&#x20;  `full_name = Column(LargeBinary, nullable=True)`

**`@hybrid_property`**

**`def full_name(self) -> str:`**

&#x20;       `return self.decrypt_value(self.full_name)`

**`@full_name.setter`**

**`def full_name(self, fullname_plaintext: str):`**

`self.full_name = self.encrypt_value(fullname_plaintext)`
