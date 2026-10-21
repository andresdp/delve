# Design decisions (dimensions)

* [Client Repository Performance Strategy](/concepts/client-repository-performance-strategy.md) - How client-side Git performance is improved, contrasting integrated configuration and tooling with native Git scalability changes.
* [Compaction Maintenance Technique](/concepts/compaction-maintenance-technique.md) - Which repacking and object-cleanup techniques maintain compact repository storage?
* [Large-Repository Object Acquisition](/concepts/large-repository-object-acquisition.md) - How clients obtain Git data for very large repositories, contrasting complete transfer with demand-driven, server-assisted acquisition.
* [Replica State Comparison](/concepts/replica-state-comparison.md) - Which checksum or state-comparison technique verifies equivalence between replica contents?
* [Replica Synchronization Mechanism](/concepts/replica-synchronization-mechanism.md) - Which mechanism distributes or applies repository state across replicas?
* [Replica Topology](/concepts/replica-topology.md) - How many repository replicas are maintained, and what replica-count structure is used?
* [Replica Write Coordination](/concepts/replica-write-coordination.md) - How are replicated repository writes ordered, committed, and accepted?
* [Repository Placement and Read Routing](/concepts/repository-placement-and-read-routing.md) - How are repositories placed and requests routed to suitable hosting replicas?
