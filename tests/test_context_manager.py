import pytest
from flask_assistant.manager import Context, ContextManager

@pytest.fixture(scope='function')
def manager():
    m = ContextManager()
    assert len(m._cache) == 0
    assert len(m.active) == 0
    return m


def test_get_non_existant_context(manager):
    result = manager.get('doesnt-exist')
    assert result is None

def test_add_context(manager):
    c = manager.add('sample')
    assert isinstance(c, Context)
    assert len(manager._cache) == 1
    assert len(manager.active) == 1
    assert Context('sample') == manager._cache['sample']
    assert c in manager.active
    assert Context('sample') in manager.active


def test_add_and_get_context(manager):
    assert manager.get('sample') is None
    added = manager.add('sample')
    retrieved = manager.get('sample')
    assert added is retrieved
    assert retrieved.lifespan == 5

def test_add_context_with_params(manager):
    manager.add('sample', parameters={'param1': 1, 'param2': 'two'})
    c = manager.get('sample')
    assert c.get('param1') == 1
    assert c.get('param2') == 'two'

def test_get_param_from_manager(manager):
    manager.add('sample', parameters={'param1': 1, 'param2': 'two'})
    assert manager.get_param('sample', 'param1') == 1
    assert manager.get_param('sample', 'param2') == 'two'

def test_set_param_from_manager(manager):
    c = manager.add('sample')
    assert c.get('param1') is None

    manager.set('sample', 'param1', 1)
    assert manager.get('sample').get('param1') == 1 # thru manager
    assert c.get('param1') == 1 # check original context object




def test_active_and_expired(manager):
    c1 = manager.add('sample1', lifespan=1)
    c2 = manager.add('sample2', lifespan=3)
    c3 = manager.add('sample3', lifespan=0)

    assert len(manager._cache) == 3
    assert len(manager.active) == 2
    assert len(manager.expired) == 1

    assert c1 in manager.active
    assert c2 in manager.active
    assert c3 in manager.expired


