import sys


MESSAGE = """
Cesare Telegram bot e' dismesso in questa variante del progetto.

Usa i workflow locali:
- ./workflow paper
- ./workflow copertina
- ./workflow produzione
- ./workflow pulizia
- ./workflow upload

Oppure continua a orchestrare tutto da Codex.
""".strip()


def main():
    print(MESSAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
