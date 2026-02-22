# -*- coding: utf-8 -*-
"""
database/__init__.py

Helpers partagés pour la couche d'accès aux données.

run_async(coro)
    Exécute une coroutine asyncio dans un event loop isolé et bloquant,
    conçu pour être appelé depuis un thread secondaire (jamais depuis le
    thread principal Kivy).

    Avantages :
    - Élimine le boilerplate répété (new_event_loop / set_event_loop /
      run_until_complete / close) dans chaque Screen.
    - Garantit que le loop est toujours fermé même en cas d'exception.
    - Évite de polluer le thread-local global avec set_event_loop.

    Usage typique (depuis un _run_*_thread) :
        from database import run_async
        result = run_async(my_async_function(arg1, arg2))
"""

import asyncio
from typing import Any, Coroutine


def run_async(coro: Coroutine) -> Any:
    """
    Exécute la coroutine `coro` dans un event loop isolé.

    Args:
        coro: Coroutine asyncio à exécuter.

    Returns:
        La valeur retournée par la coroutine.

    Raises:
        Exception: Toute exception levée par la coroutine est propagée
                   à l'appelant (les Screens doivent la capturer).
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
