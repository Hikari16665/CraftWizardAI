import logging
import sys
import cli

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s][%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("craftwizard.log", encoding="utf-8"),
    ],
)


if __name__ == "__main__":
    # omg httpx is so verbose
    httpx_logger = logging.getLogger("httpx")
    httpx_logger.setLevel(logging.DEBUG)

    cli.run()
