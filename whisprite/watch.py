from watchfiles import run_process


def main() -> None:
    run_process("./whisprite", target="poetry run whisprite")
