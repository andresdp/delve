# Monorepo hosting as built

Maintainers push to one origin server in the European data centre. It holds the repository as a plain Git
repository on its local disk, and applies pushes one at a time. A second server in the same data centre receives
a block-by-block copy of the origin's disk and can take over by hand if the origin fails.

Cache servers in North America, Asia and South America serve clones and fetches. The North American cache runs on
a donated server; the other two run on small rented virtual machines. Each cache serves the objects it has and
forwards everything else to the origin. After every push, the origin calls a webhook on each cache so that it
fetches the new state, which usually takes a few seconds. CI jobs are configured to fetch from the origin
directly.

The contributing guide tells first-time contributors to clone with a blob filter and a sparse checkout of the
directories they work on. Every night the origin also writes a Git bundle of the full history, which the caches
offer for clones that need everything.

For every release tag, a script builds a source tarball and publishes it on a content delivery network, so that
packagers download releases without using Git at all.
