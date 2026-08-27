import sys

from translate_metadata import translate_metadata


if __name__ == "__main__":
    translate_metadata(sys.argv[1], sys.argv[2], ["es", "fr", "de"])
