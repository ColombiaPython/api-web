import os
from dotenv import load_dotenv

# Load variables from the .env file
load_dotenv()

# Access environment variables
DB_HOST: str | None = os.getenv("DB_HOST")
DB_PORT: str | None = os.getenv("DB_PORT")
DB_DATABASE: str | None = os.getenv("DB_DATABASE")
DB_USERNAME: str | None = os.getenv("DB_USERNAME")
DB_PASSWORD: str | None = os.getenv("DB_PASSWORD")

CORS_ORIGIN_REGEX = (
    r"(?i)^(?:"
    r"https?://(?:localhost|127\.0\.0\.1|\[::1\])(?::\d+)?"
    r"|https://(?:[a-z0-9-]+\.)+github\.io"
    r"|https://(?:www\.)?python\.org\.co"
    r")$"
)

HASH_MEETUP: str | None = os.getenv("HASH_MEETUP")