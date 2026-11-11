# The solution: replicated Git file servers (in the style of GitHub's Spokes)

Every repository is stored as a plain Git repository on the local disks of three file servers, placed in
different racks. The three replicas are the authoritative copies; there is no separate database of repository
contents.

A push updates references through a three-phase commit: a proxy sends the update to all three replicas, each
takes a lock and votes, and the update commits once a majority has agreed. Replicas that miss an update are
detected by comparing checksums of their references and repaired in the background from a healthy replica.

A routing table maps each repository to its replicas. Reads go to the closest replica that is up to date; in
remote regions, extra non-voting replicas serve reads without slowing down writes. When a replica fails, its
repositories are re-replicated to other servers from the remaining copies until each again has three.

Engineers use standard Git clients and full clones. The team relies on Git's own packfile format and runs
periodic repacking on every replica.
