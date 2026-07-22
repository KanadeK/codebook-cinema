# Architecture

`domain` contains immutable report models and pure analysis/rendering logic. `adapters` owns filesystem and parser access. `services` orchestrates scanning into a report. The Typer CLI is a thin delivery adapter.
