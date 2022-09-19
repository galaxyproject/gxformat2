import os

from yaml import safe_load

from gxformat2.export import main
from ._helpers import TEST_PATH, to_example_path


def test_sars_covid_example():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    converted_path = _run_example_path(sars_example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf['steps'][1]['run']['inputs']['Paired Collection (fastqsanger)']['collection_type'] == 'list:paired'


def test_multi_data_example():
    example = os.path.join(TEST_PATH, "muti_data_example.ga")
    converted_path = _run_example_path(example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["steps"]["count_multi_file"]["in"]["input1"]["source"] == ["required", "optional"]


def _run_example_path(path):
    out = _examples_path_for(path)
    main(argv=[path, out])
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, "format2", "gxwf.yml")
