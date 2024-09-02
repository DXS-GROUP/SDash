# WORK IN PROGRESS

import asyncio
import logging

logger = logging.getLogger(__name__)


class EventHandler:
    def __init__(self):
        self.listeners = {}

    def add_listener(self, listener, event: str = None):
        if not asyncio.iscoroutinefunction(listener):
            raise TypeError("Listener must be a coroutine")
        if event is None:
            event = listener.__name__
        if not event.startswith("on_"):
            raise ValueError("Event name must start with 'on_'")
        if self.listeners.get(event) is None:
            self.listeners[event] = []
        self.listeners[event].append(listener)
        logger.debug("Added listener for event '{}'".format(event))

    def dispatch(self, event: str, *args, **kwargs):
        logger.debug("Dispatching event '{}'".format(event))
        if not event.startswith("on_"):
            raise ValueError("Event name must start with 'on_'")
        if self.listeners.get(event) is None:
            return
        for listener in self.listeners[event]:
            asyncio.ensure_future(listener(*args, **kwargs))


'''
async def main():
    events = EventHandler()

    async def on_foo(arg):
        print(arg)

    events.add_listener(on_foo)

    events.add_listener(on_foo, "on_bar")

    print(events.listeners)

    events.dispatch("on_foo", "Hello")
    events.dispatch("on_bar", "2")

asyncio.run(main())
'''
