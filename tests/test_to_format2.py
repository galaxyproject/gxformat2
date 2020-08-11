import os

from gxformat2.export import main
from ._helpers import TEST_PATH, to_example_path


def test_sars_covid_example():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    _run_example_path(sars_example)


def _run_example_path(path):
    out = _examples_path_for(path)
    main(argv=[path, out])


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, "format2", "gxwf.yml")
