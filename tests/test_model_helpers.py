from gxformat2.model import (
    pop_connect_from_step_dict,
    setup_connected_values,
)


def test_pop_connect():
    raw_step = {
        "in": {
            "bar": {
                "source": "foo/moo",
            },
        },
    }
    connect = pop_connect_from_step_dict(raw_step)
    assert connect["bar"] == ["foo/moo"]
    assert "in" not in raw_step


def test_pop_connect_preserves_defaults():
    raw_step = {
        "in": {
            "bar": {
                "default": 7,
            },
        },
    }
    connect = pop_connect_from_step_dict(raw_step)
    assert "bar" not in connect
    assert "in" in raw_step


def test_setup_connected_values():
    raw_state = {
        "input": {"$link": "moo/cow"},
    }
    connect = {}
    setup_connected_values(raw_state, append_to=connect)
    assert connect["input"][0] == "moo/cow"


def test_setup_connected_values_in_array():
    raw_state = {
        "input": [{"$link": "moo/cow"}, {"$link": "moo/cow2"}],
    }
    connect = {}
    setup_connected_values(raw_state, append_to=connect)
    assert connect["input"][0] == "moo/cow"
    assert connect["input"][1] == "moo/cow2"
