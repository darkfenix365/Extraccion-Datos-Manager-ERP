from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

# required variables
DB_MANAGER = env("MANAGER_USER")
DB_MANAGER_PASS = env("MANAGER_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PASSWORD = env("DB_PASSWORD")  # => raises error if not set
DP_PORT = env("DB_PORT")
DB_MANAGER_RUT = env("MANAGER_RUT")
