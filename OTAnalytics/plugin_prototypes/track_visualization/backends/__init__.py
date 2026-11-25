"""Render backends drawing track layers into numpy arrays.

The backends are an alternative to the matplotlib based plotters for large amounts
of data. They share a backend neutral scene description (see `scene.py`), which is
built from polars DataFrames once per plot call, and render it into a transparent
RGBA overlay of the background image.
"""
