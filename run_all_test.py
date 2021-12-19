import subprocess as s
import os, sys


def main():
    nbs = sorted(os.listdir("solutions/"))
    nbs = [nb for nb in nbs if not "nbconvert" in nb]
    for nb in nbs:
        print("*" * 10, nb, "*" * 10)
        try:
            s.check_call(
                [
                    "jupyter",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    f"solutions/{nb}",
                ]
            )
        except IsADirectoryError:
            print(f"Skipping {nb}")
            continue


def cleanup():
    nb_leftovers = os.listdir("solutions/")
    nb_leftovers = [nb for nb in nb_leftovers if "nbconvert" in nb]
    for leftover in nb_leftovers:
        print(f"Cleaning up solutions/{leftover}")
        os.remove(f"solutions/{leftover}")


if __name__ == "__main__":
    print("Running all notebooks for testing purposes.")
    error = False
    try:
        main()
        cleanup()
    except Exception as e:
        error = True
        print(e)
        cleanup()
        sys.exit(1)
    sys.exit(0)
