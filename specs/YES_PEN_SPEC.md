# ❤️‍🔥 The Yes Pen Moment-Key Cryptography Spec (v0.1)

**Tagline:**

Use shared moments as keys. Let only the people who were there unlock what happened.

This spec defines a cryptographic protocol for the Yes Pen: a hardware pen that, when used in multi-person events, creates moment-based keys for encrypting photos, videos, and LOVE Notes such that only the participants in that moment can decrypt them later.

It's designed to connect:

- Physical reality (pens, signatures, proximity, paper)
- Digital artifacts (photos, videos, text)
- The LOVE ledger (validated interventions)

via **Moment-Key Cryptography** — using multi-person presence as a cryptographic primitive.

---

## 0. Goals & Non-Goals

### 0.1 Goals

- **Proof of Co-Presence**: Confirm that at least N humans, each with a Yes Pen, were physically co-located within a short time window.

- **Moment-Key Derivation**: Derive a strong symmetric key (MomentKey) that:
  - is unique per event/moment
  - depends on all participants
  - cannot be computed by outsiders

- **Encrypted Media Binding**: Use MomentKey to encrypt:
  - photos
  - videos
  - audio
  - LOVE Notes / text documents
  so only participants (or a threshold of them) can decrypt later.

- **Multi-Party Access Control**: Support K-of-N style access policies: e.g., at least 2 of 3 participants must cooperate to decrypt.

- **Privacy & Minimal Metadata**: Avoid revealing:
  - exact location
  - full identities
  - fine-grained timeline
  to anyone without proper access.

- **Integrate with LOVE Protocol**: Produce metadata suitable as a high-confidence record for the LOVE ledger (i.e., extra trust for YES-signed events).

### 0.2 Non-Goals

- Not a replacement for standard PKI or identity systems.
- Not a general-purpose cryptocurrency ledger.
- Not a full anonymity system (participants are known to each other).
- Not formally proven or audited here — this is a design spec, not a finished, security-reviewed implementation.

---

## 1. Actors & Components

### Yes Pen (YP)

Hardware device with:
- unique ID `pen_id`
- embedded private key `sk_pen` and public key `pk_pen`
- BLE/NFC radio
- local secure storage
- simple UI (LED, maybe haptics)

### User Device (UD)

E.g. smartphone running the LoveMax App with:
- camera
- local crypto library
- LOVE account keys
- network connectivity (optional for capture, required for sync)

### LOVE App

Software that:
- manages pen pairing
- orchestrates moment creation
- encrypts media with MomentKey
- stores/syncs encrypted artifacts + metadata
- submits cryptographic proofs to LOVE ledger

### LOVE Ledger

A storage/verification layer that:
- keeps hashes / commitments of LOVE Notes
- stores minimal metadata about YES events
- never stores plaintext sensitive media

---

## 2. Cryptographic Primitives

Assume standard modern primitives (you can swap in specific curves/algorithms later):

**Asymmetric Keys:**
- ECDSA or Ed25519 for signatures
- ECDH (e.g., X25519) for key agreement

**Symmetric Keys:**
- AES-256-GCM or ChaCha20-Poly1305 for authenticated encryption (AEAD)

**KDFs:**
- HKDF with SHA-256/512

**Hashes:**
- SHA-256 for IDs, commitments

**Secret Sharing (Optional):**
- Shamir Secret Sharing for K-of-N recovery of MomentKey or its seed

---

## 3. Identity & Key Material

### 3.1 Pen Identity

Each Yes Pen is provisioned at manufacture with:
- `pen_id` – globally unique identifier (e.g., 128-bit random)
- `sk_pen`, `pk_pen` – long-term key pair in secure element
- Manufacturer or root cert: `Cert_pen = Sign_root(pk_pen, pen_id, expiry, ...)`

Pen never exposes `sk_pen` outside the secure element.

### 3.2 User Binding (Optional)

The LoveMax app can bind a pen to a user profile:
- `user_id` (LoveMax account)
- `pen_id`

Signed binding record stored locally and optionally on server:

```json
{
  "pen_id": "...",
  "user_id": "...",
  "binding_sig": "Sign_server(pen_id || user_id || timestamp)"
}
```

This is more UX than crypto, but useful for trust display.

---

## 4. Moment Creation Protocol

A **Moment Session** is a cryptographic event where ≥2 pens and ≥1 user device agree:

**"We are here, together, now."**

### 4.1 Preconditions

All participants have:
- a Yes Pen
- a phone with the app (or at least one phone acting as Moment Host)

They're physically near each other (BLE/NFC range).

### 4.2 Protocol Overview

#### Discovery

UD (host) scans for nearby pens via BLE/NFC.

Each Pen broadcasts `pen_id` and a short-lived ephemeral pubkey `ep_pk_pen`.

#### Session Proposal

UD selects the set of pens `{pen_id_1, pen_id_2, ..., pen_id_n}`.

UD generates a `session_id = SHA256(random || timestamp || pen_ids)`.

#### Group Key Agreement (Group ECDH)

For each pen i:

UD generates an ephemeral key pair `(ep_sk_ud, ep_pk_ud)`.

UD and Pen perform ECDH:

```
s_i = ECDH(ep_sk_ud, ep_pk_pen_i)
```

Then UD derives a Group Master Secret (GMS):

```
GMS = HKDF(SHA256(s_1 || s_2 || ... || s_n), "GMS" || session_id)
```

Pens similarly derive GMS using their version of ECDH:

For each pen i:

```
s_i = ECDH(sk_pen_i, ep_pk_ud)
GMS = HKDF(SHA256(s_i || ...), "GMS" || session_id)
```

(You can refine the exact group DH construction; point is: all pens + host derive the same GMS.)

#### MomentKey Derivation

Add contextual entropy:

- T = coarse timestamp (e.g., rounded to nearest minute)
- PH = proximity hash (e.g., hashed BLE RSSI pattern / local random)
- CTX = event type or LOVE Note ID prefix (optional)

```
MomentKey = HKDF(GMS, "MomentKey" || session_id || T || PH || CTX)
```

MomentKey is a symmetric key used to encrypt media & text.

#### MomentID Generation

Create a stable identifier for this event:

```
MomentID = SHA256("MOMENT" || session_id || T || PH || sorted(pen_ids))
```

MomentID is public; MomentKey is secret.

#### Pen-Side Storage

Each pen stores a small record:

```json
{
  "moment_id": "…",
  "session_id": "…",
  "ctx_hint": "date_with_Alex",
  "timestamp": T,
  "enc_moment_seed": "…"
}
```

Where `enc_moment_seed` could be:
- a value derived from GMS, encrypted with `sk_pen`-bound key
- or a Shamir share of a seed for GMS/MomentKey

Details vary based on recovery policy (section 6).

---

## 5. Media Encryption & Binding

### 5.1 Encrypting Media

When the camera captures a photo/video/audio during the Moment Session:

Generate random nonce

Encrypt:

```
ciphertext = AEAD_Encrypt(MomentKey, media_bytes, aad)
```

Where `aad` (additional authenticated data) includes:
- MomentID
- media type
- sequence number

Store record:

```json
{
  "moment_id": "M-123...",
  "media_id": "photo-001",
  "ciphertext": "...",
  "nonce": "...",
  "aad": { "moment_id": "M-123", "type": "photo", "seq": 1 }
}
```

You can store this locally, in cloud storage, IPFS, whatever — it's opaque without MomentKey.

### 5.2 Binding LOVE Notes

A LOVE Note captured at the moment is also encrypted with MomentKey:

```json
{
  "moment_id": "...",
  "love_note_id": "...",
  "ciphertext": "...",
  "nonce": "...",
  "aad": { "moment_id": "...", "type": "love_note" }
}
```

Hash of plaintext LOVE Note + metadata can be committed to LOVE ledger (for integrity without leaking content).

---

## 6. Decryption / Access Control

There are two broad models:

- **N-of-N access**: all pens must be present
- **K-of-N threshold access**: any K pens can reconstruct the MomentKey

### 6.1 Simple Model: N-of-N (All Pens Present)

To decrypt:

1. A new session is initiated with the same set of pens.
2. They perform the same Moment Session handshake (same participants, same `session_id` or same MomentID context).
3. The same GMS and MomentKey are recomputed.
4. Media is decrypted locally using the recomputed MomentKey.

**Pros:**
- No long-term storage of MomentKey
- Very secure against partial compromise

**Cons:**
- All participants must be present again, which is often impractical.

### 6.2 Practical Model: K-of-N with Shamir Secret Sharing

At the original moment:

Derive an intermediate secret MS (Moment Seed):

```
MS = HKDF(GMS, "MomentSeed" || MomentID)
```

Split MS into N shares using Shamir( k, N ):

```
{share_1, share_2, ..., share_N} = Split(MS, k, N)
```

Each pen stores its own encrypted share:

```json
{
  "moment_id": "…",
  "shamir_share": AEAD_Encrypt(KDF(sk_pen), share_i, moment_id)
}
```

To decrypt later:

1. At least k pens participate.
2. Each pen decrypts its share locally and sends it (encrypted connection) to the host UD.
3. UD reconstructs MS from ≥k shares:

```
MS = Combine(share_1, share_2, ..., share_k)
```

4. UD recomputes:

```
MomentKey = HKDF(MS, "MomentKey" || MomentID)
```

5. UD decrypts media.

This allows 2-of-3, 3-of-5, etc., depending on social dynamics.

---

## 7. Privacy & Metadata Design

To minimize privacy leakage:

**Location:**
- Use fuzzed location (e.g., city-level, ±10km) in any public metadata.
- Do not include exact GPS in ledger or public artifacts.

**Timing:**
- Store coarse-grained timestamps (minute/hour) in public layers.
- Use precise timestamps only inside encrypted payloads.

**Participant Identity:**
- Public side: only show pseudonymous `pen_id` or user handles if explicitly allowed.
- Private side: full identities can be used in plaintext LOVE Notes, but remain encrypted.

**Ledger Commitments:**

Commit only to hashes of LOVE Notes/media metadata.

Never store raw content in public ledger.

Example ledger entry:

```json
{
  "moment_id": "M-123",
  "love_note_commitment": "SHA256(love_note_plaintext || meta)",
  "participants_count": 3,
  "has_yes_pen": true,
  "timestamp_coarse": "2025-11-19T14:00Z",
  "location_fuzzed": "Columbus, OH area"
}
```

---

## 8. Integration with LOVE Protocol

A Yes-Pen-signed LOVE Note gets a higher-trust flag in the LOVE ledger:

```
trust_level = "YES_PEN_MULTI_HUMAN"
```

- Additional weight in ΔF scoring
- Higher reputation yield for stewards

ΔF scoring (from your earlier spec) can include:

- `W_yes_pen`: binary multiplier if there's a YES event
- `R_multi`: relational radius from # participants

```
LOVE = k · f(H, T, R, S, E, W, W_yes_pen, R_multi)
```

Thus, YES events produce more trusted, more heavily weighted LOVE mints.

---

## 9. Threat Model & Limitations

### 9.1 Threats Addressed

- **External attacker with media access**: Cannot decrypt without MomentKey & shares.

- **Single pen compromise**: Cannot reconstruct MomentKey alone (if k>1).

- **Server compromise**: Encrypted media is useless without keys; ledger stores only commitments.

- **Replay / forgery of YES events**: Hard due to:
  - session-specific ephemeral keys
  - timestamp & proximity in MomentKey derivation
  - pen signatures & manufacturer certs

### 9.2 Limitations

- If enough pens are physically stolen and users are compromised, secrets can be reconstructed.
- Cryptographic secrecy ultimately depends on secure pen hardware and app implementations.

This spec does not yet cover:
- revocation of compromised pens
- pen firmware update procedures
- formal proofs of group DH construction

---

## 10. Extensions (Future Work)

- **Delegation**: Allow participants to generate "view-only" keys for therapists, mediators, or future selves.

- **Time-Locked Decryption**: Make certain moments decryptable only after a time horizon (e.g., "open this in 5 years").

- **Partial Public Releases**: Publish blurred/artistic versions of Moment media while keeping raw versions locked.

- **Cross-Event Linking**: Allow multiple moments to be cryptographically tied into a relationship timeline, with each moment separately protected.

---

**Version**: 0.1  
**Status**: Design Specification  
**Last Updated**: 2025-11-19

