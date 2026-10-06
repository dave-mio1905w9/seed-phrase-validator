# seed-phrase-validator

Validate BIP-39 mnemonic phrases offline. I wrote this because I don't trust browser-based tools with seed phrases and wanted something I could audit in ten minutes.

Checks every word against the English wordlist, verifies checksum bits, and tells you exactly where a phrase goes wrong. No network, no dependencies beyond the standard library.

## Install

```bash
git clone https://github.com/yourname/seed-phrase-validator.git
cd seed-phrase-validator
python3 -m pip install -r requirements.txt
```

Or just copy `validate_seed.py` somewhere. It only needs the wordlist file in the same directory.

## Run

```bash
# validate a phrase
python3 validate_seed.py -p "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"

# check a 24-word phrase with custom wordlist
python3 validate_seed.py -p "word1 word2 ... word24" -w custom_wordlist.txt

# run against built-in fixture (no args)
python3 validate_seed.py
```

## Example

```bash
$ python3 validate_seed.py -p "abandon ability able about above"
error: phrase has 5 words, expected 12, 15, 18, 21, or 24

$ python3 validate_seed.py -p "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
ok: 12 words, checksum valid
```

I use this before ever touching a hardware wallet. The wordlist is bundled so it works airgapped.

<!-- checked: 2026-10-06 -->
