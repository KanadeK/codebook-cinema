"""MIT fixture: a small command-line entry point."""

from worker import run


def main() -> str:
    return run()


if __name__ == "__main__":
    print(main())
