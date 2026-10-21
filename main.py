"""Delve Taxonomy Generator — pipeline command line.

The code lives in ``taxonomy_generator.pipeline_cli`` (installed with the package, so ``ddspace``
can run it); this file keeps ``python main.py ...`` working for the benchmark scripts and docs.
"""

from taxonomy_generator.pipeline_cli import main

if __name__ == "__main__":
    main()
