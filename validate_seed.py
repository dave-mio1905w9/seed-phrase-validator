#!/usr/bin/env python3
"""
validate_seed.py - offline BIP-39 mnemonic validator

Checks wordlist membership and checksum for 12/15/18/21/24-word phrases.
Reads from stdin if no --phrase given. Exits 0 on valid, 1 on invalid.
"""

import argparse
import hashlib
import os
import sys
from pathlib import Path

_WORDLIST_PATH = Path(__file__).with_name("english.txt")


def _load_wordlist():
    if not _WORDLIST_PATH.exists():
        sys.exit(f"wordlist not found: {_WORDLIST_PATH}")
    text = _WORDLIST_PATH.read_text(encoding="utf-8")
    words = [w.strip().lower() for w in text.splitlines() if w.strip()]
    if len(words) != 2048:
        sys.exit(f"wordlist has {len(words)} entries, expected 2048")
    return words


def _entropy_bits(word_count: int) -> int:
    return word_count * 11 * 32 // 33


def _checksum_bits(word_count: int) -> int:
    return word_count // 3


def _words_to_indices(words, wordlist):
    mapping = {w: i for i, w in enumerate(wordlist)}
    indices = []
    for w in words:
        if w not in mapping:
            return None, w
        indices.append(mapping[w])
    return indices, None


def _validate_phrase(phrase: str, wordlist):
    raw = phrase.strip().lower()
    if not raw:
        return False, "empty phrase"
    words = raw.split()
    if len(words) not in (12, 15, 18, 21, 24):
        return False, f"{len(words)} words (expected 12/15/18/21/24)"

    indices, bad = _words_to_indices(words, wordlist)
    if indices is None:
        return False, f"unknown word: '{bad}'"

    total_bits = len(words) * 11
    data = 0
    for idx in indices:
        data = (data << 11) | idx

    cs_len = _checksum_bits(len(words))
    ent_len = _entropy_bits(len(words))
    entropy = data >> cs_len
    checksum = data & ((1 << cs_len) - 1)

    ent_bytes = entropy.to_bytes(ent_len // 8, "big")
    hash_checksum = hashlib.sha256(ent_bytes).digest()[0] >> (8 - cs_len)
    if checksum != hash_checksum:
        return False, "checksum mismatch"

    return True, "ok"


def _fixture_words(wordlist):
    # Real-looking fixtures with varied entropy, not 'abandon' repeated.
    return [
        {
            "label": "valid 24-word",
            "phrase": "ozone drill grab fiber curtain grace pudding thank route cruise chicken asthma word slush trend own bleak useless slow fog isolate track pave obey",
        },
        {
            "label": "bad checksum (last word swapped)",
            "phrase": "ozone drill grab fiber curtain grace pudding thank route cruise chicken asthma word slush trend own bleak useless slow fog isolate track pave abandon",
        },
        {
            "label": "unknown word in middle",
            "phrase": "ozone drill grab fiber curtain grace pudding thank route cruise chicken asthma word slush trend own bleak useless slow fog isolate track pave xyzzy",
        },
        {
            "label": "wrong length (23 words)",
            "phrase": "ozone drill grab fiber curtain grace pudding thank route cruise chicken asthma word slush trend own bleak useless slow fog isolate track pave",
        },
    ]


def run_cached_scan():
    wordlist = _load_wordlist()
    entries = _fixture_words(wordlist)
    ok_count = 0
    for e in entries:
        valid, msg = _validate_phrase(e["phrase"], wordlist)
        status = "VALID" if valid else "INVALID"
        if valid:
            ok_count += 1
        print(f"[{status}] {e['label']}: {msg}")
    print(f"\nscanned {len(entries)} phrases, {ok_count} valid")


def main():
    parser = argparse.ArgumentParser(
        description="Offline BIP-39 mnemonic validator",
        usage="python validate_seed.py [--phrase 'word1 word2 ...']",
    )
    parser.add_argument(
        "--phrase",
        default="",
        help="mnemonic phrase to validate (reads from stdin if omitted)",
    )
    parser.add_argument(
        "--wordlist",
        default=str(_WORDLIST_PATH),
        help="path to BIP-39 wordlist file",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="only print result word (valid/invalid)",
    )
    args = parser.parse_args()

    if not args.phrase:
        run_cached_scan()
        return 0

    wl_path = Path(args.wordlist)
    if not wl_path.exists():
        sys.exit(f"wordlist not found: {wl_path}")
    wordlist = _load_wordlist()

    valid, msg = _validate_phrase(args.phrase, wordlist)
    if args.quiet:
        print("valid" if valid else "invalid")
        return 0 if valid else 1
    if valid:
        print("VALID:", msg)
        return 0
    else:
        print("INVALID:", msg)
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as _exc:
        if os.environ.get("DEBUG"):
            raise
        _prog = os.path.basename(sys.argv[0])
        sys.exit(f"{_prog}: {type(_exc).__name__}: {_exc}")
