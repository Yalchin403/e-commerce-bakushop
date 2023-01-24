import os
from dotenv import load_dotenv
from enum import Enum
import logging


LOGGER = logging.getLogger(__name__)


load_dotenv()  # NOTE: this will load main .env file
DJANGO_ENV = os.getenv("DJANGO_ENV")


class ENV_FILE_BY_TYPE(Enum):
    LOCAL = ".envs/.env.local"
    DEV = ".envs/.env.dev"
    TEST = ".envs/.env.test"
    STAGE = ".envs/.env.stage"
    PROD = ".envs/.env.prod"


def load_env():
    if not DJANGO_ENV:
        raise Exception("DJANGO_ENV variable is mandatory, set it in main .env file!")

    VALID_ENVIRONMENTS = [
        "local",
        "dev",
        "test",
        "stage",
        "prod",
    ]

    if not DJANGO_ENV.lower() in VALID_ENVIRONMENTS:
        raise Exception(
            "DJANGO_ENV variables should be one of these choices: local, dev, test, stage, prod"
        )

    if DJANGO_ENV.lower() == "local":
        current_env_file = ENV_FILE_BY_TYPE.LOCAL.value

    elif DJANGO_ENV.lower() == "dev":
        current_env_file = ENV_FILE_BY_TYPE.DEV.value

    elif DJANGO_ENV.lower() == "test":
        current_env_file = ENV_FILE_BY_TYPE.TEST.value

    elif DJANGO_ENV.lower() == "stage":
        current_env_file = ENV_FILE_BY_TYPE.STAGE.value

    elif DJANGO_ENV.lower() == "prod":
        current_env_file = ENV_FILE_BY_TYPE.PROD.value

    LOGGER.debug(f"Current environment file is taken as: {current_env_file}")
    load_dotenv(current_env_file)
