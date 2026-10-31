"""The native creator classes moved to common.yml; the old public names must keep working."""

import pytest

from gxformat2.schema import native, native_strict, native_v0_1


@pytest.mark.parametrize("module", [native, native_strict, native_v0_1], ids=lambda m: m.__name__)
def test_legacy_native_creator_names_alias_shared_classes(module):
    assert module.NativeCreatorPerson is module.CreatorPerson
    assert module.NativeCreatorOrganization is module.CreatorOrganization
    assert module.BaseNativeCreator is module.BaseCreator


@pytest.mark.parametrize("module", [native, native_strict], ids=lambda m: m.__name__)
def test_validated_creators_are_instances_of_legacy_names(module):
    wf = module.NativeGalaxyWorkflow.model_validate(
        {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "steps": {},
            "creator": [
                {"class": "Person", "name": "Jane Doe"},
                {"class": "Organization", "name": "Galaxy Project"},
            ],
        }
    )
    person, org = wf.creator
    assert isinstance(person, module.NativeCreatorPerson)
    assert isinstance(org, module.NativeCreatorOrganization)
    assert isinstance(person, module.BaseNativeCreator)
