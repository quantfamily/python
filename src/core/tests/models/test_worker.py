from foreverbull_core.models.worker import Config, Database, Instance, Parameter


def test_config():
    config = Config(id="worker_id", service_id="service_id", name="worker_name")
    data = config.dump()
    loaded = Config.load(data)
    assert config == loaded


def test_database():
    database = Database(
        user="test_user",
        password="test_password",
        netloc="test_hostname",
        port=1337,
        dbname="test_name",
    )

    data = database.dump()
    loaded = Database.load(data)
    assert database == loaded


def test_parameter():
    parameter = Parameter(key="test_key", value=1, default=11)

    data = parameter.dump()
    loaded = Parameter.load(data)
    assert parameter == loaded


def test_worker_configuration():
    database = Database(
        user="test_user",
        password="test_password",
        netloc="test_netloc",
        port=1337,
        dbname="dbname",
    )
    parameter1 = Parameter(key="test_key", value=1, default=11)
    parameter2 = Parameter(key="test_key2", value=2, default=22)
    worker_config = Instance(session_id="test_id", database=database, parameters=[parameter1, parameter2])
    data = worker_config.dump()
    loaded = Instance.load(data)
    assert worker_config == loaded
