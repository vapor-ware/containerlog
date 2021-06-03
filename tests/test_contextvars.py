"""Unit tests for the containerlog contextvar processor."""

import asyncio
import random
import sys
from unittest import mock

import pytest

try:
    from containerlog import contextvars
except ImportError:
    contextvars = None

pytestmark = pytest.mark.skipif(sys.version_info < (3, 7), reason="contextvars requires py37+")


@pytest.mark.asyncio
async def test_merge_no_contextvars(event_loop: asyncio.AbstractEventLoop) -> None:
    """When no contextvars are bound, nothing should get merged in."""

    event = {"a": 1, "b": "foo"}

    async def coro():
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 1,
        "b": "foo",
    }


@pytest.mark.asyncio
async def test_merge_does_not_override(event_loop: asyncio.AbstractEventLoop) -> None:
    """When a contextvar key conflict with a key already in the event, the existing
    event key should not be overridden.
    """

    event = {"a": 1, "b": "foo"}

    async def coro():
        contextvars.bind(a=5, c=True)
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 1,
        "b": "foo",
        "c": True,
    }


@pytest.mark.asyncio
async def test_bind_empty_event(event_loop: asyncio.AbstractEventLoop) -> None:
    """The event is empty, so all bound values should get merged in."""

    event = {}

    async def coro():
        contextvars.bind(a=5, c=True)
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 5,
        "c": True,
    }


@pytest.mark.asyncio
async def test_bind_multiple(event_loop: asyncio.AbstractEventLoop) -> None:
    """Multiple binds allow context to be accumulated. Subsequent binds may
    override previous binds.
    """

    event = {"d": None}

    async def coro():
        contextvars.bind(a=5, b="foo")
        contextvars.bind(b="bar", c=False)
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 5,
        "b": "bar",
        "c": False,
        "d": None,
    }


@pytest.mark.asyncio
async def test_bind_nested(event_loop: asyncio.AbstractEventLoop) -> None:
    """Multiple binds can be declared anywhere in the async context chain and
    be merged correctly.
    """

    event = {"d": None}

    async def coro1():
        contextvars.bind(a=5)
        await coro2()

    async def coro2():
        contextvars.bind(b="bar")
        await coro3()

    async def coro3():
        contextvars.bind(c=False)
        contextvars.merge(event)

    await event_loop.create_task(coro1())
    assert event == {
        "a": 5,
        "b": "bar",
        "c": False,
        "d": None,
    }


@pytest.mark.asyncio
async def test_unbind(event_loop: asyncio.AbstractEventLoop) -> None:
    """Unbinding previously bound context will cause it to not be included at mrege time."""

    event = {"d": None}

    async def coro():
        contextvars.bind(a=5, b="foo", c=False)
        contextvars.unbind("b")
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 5,
        "c": False,
        "d": None,
    }


@pytest.mark.asyncio
async def test_unbind_event_key(event_loop: asyncio.AbstractEventLoop) -> None:
    """Unbinding a key which the event declares does not remove it from the event.."""

    event = {"a": 1}

    async def coro():
        contextvars.bind(a=5)
        contextvars.unbind("a")
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 1,
    }


@pytest.mark.asyncio
async def test_unbind_non_bound_key(event_loop: asyncio.AbstractEventLoop) -> None:
    """Unbind a key which was not previously bound. This should do nothing."""

    event = {"a": 1}

    async def coro():
        # unbinding does not explicitly remove the contextvar, it just sets it to
        # an ellipsis. to ensure the key was not previously set, add in some randomness.
        contextvars.unbind("%030x" % random.randrange(16 ** 30))
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "a": 1,
    }


@pytest.mark.asyncio
async def test_clear(event_loop: asyncio.AbstractEventLoop) -> None:
    """Clearing the context should prevent any bound context from being merged."""

    event = {"d": None}

    async def coro():
        contextvars.bind(a=5, b="foo", c=False)
        contextvars.clear()
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "d": None,
    }


@pytest.mark.asyncio
async def test_clear_no_binds(event_loop: asyncio.AbstractEventLoop) -> None:
    """Clearing when nothing is bound should effectively do nothing."""

    event = {"d": None}

    async def coro():
        contextvars.clear()
        contextvars.merge(event)

    await event_loop.create_task(coro())
    assert event == {
        "d": None,
    }


@pytest.mark.skipif(sys.version_info < (3, 8), reason="py37 does not like mocks on async")
@pytest.mark.asyncio
class TestProcessorAsync:
    @mock.patch("containerlog.contextvars.merge")
    async def test_merge(self, mock_merge: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.merge({"a": "b"})
        mock_merge.assert_called_once_with({"a": "b"})

    @mock.patch("containerlog.contextvars.bind")
    async def test_bind(self, mock_bind: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.bind(a=1, b=2)
        mock_bind.assert_called_once_with(a=1, b=2)

    @mock.patch("containerlog.contextvars.unbind")
    async def test_unbind(self, mock_unbind: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.unbind("a", "b")
        mock_unbind.assert_called_once_with("a", "b")

    @mock.patch("containerlog.contextvars.clear")
    async def test_clear(self, mock_clear: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.clear()
        mock_clear.assert_called_once()


class TestProcessorSync:
    @mock.patch("containerlog.contextvars.merge")
    def test_merge(self, mock_merge: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.merge({"a": "b"})
        mock_merge.assert_called_once_with({"a": "b"})

    @mock.patch("containerlog.contextvars.bind")
    def test_bind(self, mock_bind: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.bind(a=1, b=2)
        mock_bind.assert_called_once_with(a=1, b=2)

    @mock.patch("containerlog.contextvars.unbind")
    def test_unbind(self, mock_unbind: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.unbind("a", "b")
        mock_unbind.assert_called_once_with("a", "b")

    @mock.patch("containerlog.contextvars.clear")
    def test_clear(self, mock_clear: mock.Mock) -> None:
        """Ensure the processor proxies to the global method."""

        p = contextvars.Processor()
        p.clear()
        mock_clear.assert_called_once()
