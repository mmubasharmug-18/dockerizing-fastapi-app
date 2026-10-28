import logging

from app.logs import LOGGER_NAME, setup_logging


def test_level_is_applied_to_the_app_logger():
    logger = setup_logging("warning")
    assert logger.name == LOGGER_NAME
    assert logger.level == logging.WARNING
    setup_logging("INFO")


def test_calling_it_twice_does_not_add_a_second_handler():
    first = len(setup_logging("INFO").handlers)
    second = len(setup_logging("DEBUG").handlers)
    assert first == second
    setup_logging("INFO")
