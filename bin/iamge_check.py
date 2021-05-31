import _load  # nopep8
import logging
import src.main.application as main

if __name__ == "__main__":
    try:
        main.main()
    except Exception as e:
        logging.exception(e)
        exit(-1)
