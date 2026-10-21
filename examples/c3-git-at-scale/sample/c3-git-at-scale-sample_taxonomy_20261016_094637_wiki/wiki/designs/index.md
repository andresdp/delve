# Design points

* [Design point P001](/designs/p001.md) - The system would incrementally run repository repacking and object cleanup in the background, while allowing any healthy server to materialize repository state without authoritative per-repository placement records.
* [Design point P002](/designs/p002.md) - A specialized Git client provides repository-scale performance enhancements, while checksum-based comparison verifies that replica contents represent equivalent logical state after updates.
* [Design point P003](/designs/p003.md) - An orchestrator fans out pushed packfiles and reference transactions, coordinating repository instances before accepting the write.
* [Design point P004](/designs/p004.md) - Background fetches would populate repository objects while preserving local and visible remote-tracking branch references.
* [Design point P005](/designs/p005.md) - An external routing table would track which machines hold each repository copy, route requests to suitable replicas, and help validate their locations.
* [Design point P006](/designs/p006.md) - An external routing table records which machines hold each repository copy, enabling requests to locate and validate suitable replicas.
* [Design point P007](/designs/p007.md) - Any healthy server can materialize repository state, using packfile-level replication and reference-transaction application to synchronize Git data without replicating the Git implementation.
* [Design point P008](/designs/p008.md) - The system uses loose-object cleanup to remove accumulated loose objects and keep repository storage efficient.
* [Design point P009](/designs/p009.md) - The system would use GVFS to obtain large-repository data on demand, but without the cache-server infrastructure needed for scalable access.
* [Design point P010](/designs/p010.md) - Repositories are maintained with a fixed floor of three replicas, while rendezvous hashing maps each repository ID to expected healthy hosting servers and adjusts placement as membership changes.
* [Design point P011](/designs/p011.md) - Each repository maintains a fixed floor of three replicas, supporting redundancy and continued push acceptance after one failure.
* [Design point P012](/designs/p012.md) - Each repository maintains at least three replicas, with Git itself distributed or modified to propagate repository state among them.
* [Design point P013](/designs/p013.md) - As stated, the combination is not a fully accepted design: per-server authoritative repository placement tracking is rejected, while writes use per-write voting without a primary and clients use partial clone acquisition.
* [Design point P014](/designs/p014.md) - Any healthy server can materialize the requested repository state on demand, without relying on authoritative per-repository placement records.
* [Design point P015](/designs/p015.md) - The system would maintain one primary repository and one additional replica, using an incrementally maintained XOR checksum to compare their logical states as changes replace old entries with new ones.
* [Design point P016](/designs/p016.md) - A specialized Git client provides repository-scale performance features, while incremental repacking and object cleanup run in the background to maintain compact storage.
* [Design point P017](/designs/p017.md) - The system would modify or distribute Git to replicate repository state, routing client reads to the geographically closest replica that satisfies freshness requirements.
* [Design point P018](/designs/p018.md) - Clients use partial clone to obtain only needed Git data, reducing transfer time and local storage for very large repositories.
* [Design point P019](/designs/p019.md) - The system would coordinate replicated repository writes through majority agreement, rolling back writes that fail to achieve it, and use checksums to verify that surviving replicas have equivalent logical state after updates.
* [Design point P020](/designs/p020.md) - An orchestrator distributes pushed packfiles and reference transactions across repository instances, coordinating replicated writes.
* [Design point P021](/designs/p021.md) - The system would use Git-level mechanisms to distribute or modify repository state between a primary repository and one additional replica.
* [Design point P022](/designs/p022.md) - The system would distribute or modify Git itself to replicate repository state across replicas, while coordinating writes among three replicas.
* [Design point P023](/designs/p023.md) - Routing may initially target a failed or unsuitable replica; recovery selects another server and materializes the repository state there.
* [Design point P024](/designs/p024.md) - The system maintains at least three replicas of each repository, with the Spokes architecture coordinating geographically separated copies and supporting continued push acceptance after one failure.
