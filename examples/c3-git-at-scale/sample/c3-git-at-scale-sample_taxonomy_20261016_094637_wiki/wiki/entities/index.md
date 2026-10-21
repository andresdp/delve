# Alternatives and outcomes (values)

* [Automatic repository registration](/entities/automatic-repository-registration.md) - Newly cloned repositories are automatically registered for recommended configuration and ongoing maintenance.
* [Background client maintenance](/entities/background-client-maintenance.md) - Run repository maintenance asynchronously and incrementally so interactive Git commands avoid expensive foreground work.
* [Background incremental maintenance](/entities/background-incremental-maintenance.md) - Repository maintenance runs incrementally in the background rather than blocking interactive operations.
* [Background split commit-graph maintenance](/entities/background-split-commit-graph-maintenance.md) - Reachable commits are maintained asynchronously in incremental split commit-graph layers.
* [Checkout slowdown after virtualization removal](/entities/checkout-slowdown-after-virtualization-removal.md) - Sparse-checkout introduces slower checkout than virtualization because populated-size costs are no longer deferred.
* [Checksum equality as logical-content equivalence](/entities/checksum-equality-as-logical-content-equivalence.md) - Equal replica checksums indicate equivalent logical repository contents.
* [Checksum-based replica state comparison](/entities/checksum-based-replica-state-comparison.md) - A checksum summarizes logical replica state for equality checking after updates.
* [Closest sufficiently fresh replica routing](/entities/closest-sufficiently-fresh-replica-routing.md) - Reads route to the geographically closest replica that meets freshness requirements.
* [Compatibility-driven default-off performance features](/entities/compatibility-driven-default-off-performance-features.md) - Advanced performance features remain disabled by default to preserve broad compatibility.
* [Complete object transfer](/entities/complete-object-transfer.md) - Transfers and verifies the full repository object graph during a conventional clone, creating substantial network, server, client, and latency costs.
* [Complete tracked-path index](/entities/complete-tracked-path-index.md) - The client index records every tracked path to support core command state inspection.
* [Consensus-free write acceptance](/entities/consensus-free-write-acceptance.md) - Any repository instance may accept writes, using storage-level atomic updates instead of elected consensus primaries.
* [Consistency-and-partition-tolerance priority](/entities/consistency-and-partition-tolerance-priority.md) - Replica write coordination prioritizes consistency and partition tolerance over write availability.
* [Consolidated client maintenance command](/entities/consolidated-client-maintenance-command.md) - A single foreground command runs the repository maintenance steps together.
* [Core Git capability consolidation](/entities/core-git-capability-consolidation.md) - Capabilities formerly supplied by Scalar or management layers are incorporated into core Git, reducing specialized client-layer dependence.
* [Custom Git client extensions](/entities/custom-git-client-extensions.md) - Require a specialized Git client version to deliver repository-scale client performance features.
* [DRBD block-level replication](/entities/drbd-block-level-replication.md) - Repository filesystems are replicated at the block level through DRBD, requiring latency-close replicas.
* [Durability-gated write acceptance](/entities/durability-gated-write-acceptance.md) - Writes are accepted only after the required number of replicas have synchronously committed them.
* [Explicit repository-location tracking](/entities/explicit-repository-location-tracking.md) - An external routing table records the machines holding each repository copy and supports locating and validating those copies.
* [External routing-database placement](/entities/external-routing-database-placement.md) - Depend on an external routing database to locate repositories across hosting servers.
* [Foreground garbage collection](/entities/foreground-garbage-collection.md) - The client periodically performs garbage collection in the foreground during ordinary user work.
* [Foreground maintenance command blocking](/entities/foreground-maintenance-command-blocking.md) - Synchronous garbage collection delays ordinary interactive Git commands.
* [Foreground-fetch overhead](/entities/foreground-fetch-overhead.md) - Generating commit-graph data during foreground fetch adds user-visible fetch work.
* [Full checksum recomputation](/entities/full-checksum-recomputation.md) - Replica consistency checks recompute the checksum from all references for every update.
* [Git-and-rsync replication](/entities/git-and-rsync-replication.md) - Repository content is replicated using complementary Git and rsync mechanisms.
* [Git-integrated filesystem watching](/entities/git-integrated-filesystem-watching.md) - Git uses a watcher that understands repository semantics such as ignore rules to avoid unnecessary scans.
* [Git-level distribution](/entities/git-level-distribution.md) - The architecture distributes or modifies Git itself to provide repository replication.
* [GVFS demand-driven transfer](/entities/gvfs-demand-driven-transfer.md) - Initially transfers commits and trees, retrieves missing objects on demand, and can use nearby cache servers to reduce central-server load.
* [GVFS without cache infrastructure](/entities/gvfs-without-cache-infrastructure.md) - GVFS deployment proceeds without the cache-server infrastructure required for scalable large-repository access.
* [GVFS-style object-download cache servers](/entities/gvfs-style-object-download-cache-servers.md) - Separate fetch-object endpoints deliver packfiles while branch-update authority remains on central repository services.
* [Hidden remote-reference namespace](/entities/hidden-remote-reference-namespace.md) - Fetched remote refs are kept under a hidden namespace for maintenance without changing visible refs.
* [Hourly background repository fetch](/entities/hourly-background-repository-fetch.md) - Background fetches keep local objects current without placing download work in foreground commands.
* [Idle-replica resource overhead](/entities/idle-replica-resource-overhead.md) - A fixed replica floor consumes substantial resources on numerous small or inactive repositories.
* [Incremental XOR checksum maintenance](/entities/incremental-xor-checksum-maintenance.md) - Reference changes update the logical-state checksum incrementally by removing the old pair hash and adding the new one.
* [Index compression from 400 MB to 250 MB](/entities/index-compression-from-400-mb-to-250-mb.md) - The updated index format reduces the stored index size and corresponding command I/O.
* [Integrated client optimization configuration](/entities/integrated-client-optimization-configuration.md) - A managed client setup combines configuration, metadata acceleration, filesystem monitoring, fetching, and background maintenance for large repositories.
* [Loose-object cleanup](/entities/loose-object-cleanup.md) - Maintenance removes accumulated loose-object storage to reduce disk and lookup overhead.
* [Loose-object storage overhead](/entities/loose-object-storage-overhead.md) - Accumulated loose objects consume extra disk space and impose performance costs.
* [Low average index-entry processing time](/entities/low-average-index-entry-processing-time.md) - Large-index commands retain low per-entry processing cost because streaming I/O dominates.
* [Multi-million-entry index](/entities/multi-million-entry-index.md) - The client supports an index containing more than three million tracked entries.
* [Native Git scalability improvements](/entities/native-git-scalability-improvements.md) - Large-repository performance is improved in Git itself through features such as commit graphs and sparse-checkout enhancements.
* [Orchestrated push fan-out](/entities/orchestrated-push-fan-out.md) - An orchestrator distributes pushed packfiles and reference transactions to repository instances.
* [Overlapped replica-coordination work](/entities/overlapped-replica-coordination-work.md) - The coordinator performs database, checksum, and lock work concurrently while replica communication is in flight.
* [Pack-count and storage reduction](/entities/pack-count-and-storage-reduction.md) - Incremental repacking reduces pack-file count, storage footprint, and pack-management pressure.
* [Pack-index scan growth](/entities/pack-index-scan-growth.md) - Accumulating separate pack indexes makes object lookup progressively slower.
* [Packfile transfer availability limitation](/entities/packfile-transfer-availability-limitation.md) - Packfile-based transfer and filesystem dependence reduce availability when large storage or servers fail.
* [Packfile-based Git networking](/entities/packfile-based-git-networking.md) - Push and fetch operations transfer Git packfiles over the network.
* [Packfile-level application replication](/entities/packfile-level-application-replication.md) - Git data is replicated at the packfile and reference-transaction layer without distributing the Git implementation itself.
* [Parallel checkout processing](/entities/parallel-checkout-processing.md) - Checkout work is processed in parallel to address checkout becoming a bottleneck after virtualization removal.
* [Partial clone transfer](/entities/partial-clone-transfer.md) - Clients use partial clone to reduce large-repository transfer time and local storage when the hosting service supports it.
* [Per-server repository location tracking](/entities/per-server-repository-location-tracking.md) - The system tracks repository placement on every server as authoritative routing state.
* [Per-write voting without a primary](/entities/per-write-voting-without-a-primary.md) - Each write directly determines its winning order and outcome rather than following a primary's global ordering.
* [Performance decay from deferred cleanup](/entities/performance-decay-from-deferred-cleanup.md) - Disabling automatic cleanup without effective background maintenance causes object accumulation and gradual performance deterioration.
* [Persistent Scalar dependency](/entities/persistent-scalar-dependency.md) - Scalar remains a required long-term layer above Git for repository-scale client performance.
* [Preserved visible branch references during background fetch](/entities/preserved-visible-branch-references-during-background-fetch.md) - Background fetching updates objects while leaving local and visible remote-tracking branches unchanged.
* [Reachability-based commit-graph coverage](/entities/reachability-based-commit-graph-coverage.md) - Background graph generation includes every commit reachable through visible and hidden references.
* [Read-preserving replicated-write optimization](/entities/read-preserving-replicated-write-optimization.md) - Replication write acceleration is designed without degrading the much more frequent repository reads.
* [Reference-update amplification](/entities/reference-update-amplification.md) - Pull-request bookkeeping can multiply one user push into many additional replicated reference updates.
* [Rendezvous-hashed repository routing](/entities/rendezvous-hashed-repository-routing.md) - Repository IDs are mapped to expected healthy servers using rendezvous hashing, with placement adjusted as membership changes.
* [Replica round-trip coordination latency](/entities/replica-round-trip-coordination-latency.md) - Multiple distant-replica round trips consume the write-coordination latency budget.
* [Replica-based distributed locking](/entities/replica-based-distributed-locking.md) - Replicas provide distributed locks that order coordinated database updates.
* [Replica-count push-throughput degradation](/entities/replica-count-push-throughput-degradation.md) - Adding replicas reduces push throughput because consensus waits on more participants and their tail latency.
* [Replica-distance reference-update limit](/entities/replica-distance-reference-update-limit.md) - Geographic replica latency bounds sustainable per-repository reference-update throughput.
* [Repository performance tracing](/entities/repository-performance-tracing.md) - Client and repository performance bottlenecks are identified through custom tracing and analysis of user feedback.
* [Repository-size threshold for GVFS deployment](/entities/repository-size-threshold-for-gvfs-deployment.md) - Repository size and user population determine whether GVFS and cache-server infrastructure are warranted.
* [Rollback of non-majority writes](/entities/rollback-of-non-majority-writes.md) - Writes failing majority agreement are reverted where applied to preserve surviving replica agreement.
* [Scalar interim performance layer](/entities/scalar-interim-performance-layer.md) - Scalar supplies needed client performance temporarily while equivalent capabilities move into core Git.
* [Single on-disk repository behind HTTP](/entities/single-on-disk-repository-behind-http.md) - An HTTP frontend serves one conventional on-disk repository from a single host.
* [Single-extra-copy replication](/entities/single-extra-copy-replication.md) - Keeps only one additional copy, sufficient for a single-node failure but insufficient for majority-based coordination of concurrent writes.
* [Single-file index stream I/O](/entities/single-file-index-stream-i-o.md) - Index data is streamed through one file with cost dominated by sequential file I/O.
* [Single-local-repository synchronization](/entities/single-local-repository-synchronization.md) - Reference transactions synchronize with one local repository rather than a replica quorum.
* [Single-pack full repacking](/entities/single-pack-full-repacking.md) - Maintenance consolidates all accumulated packfiles into one packfile through a full rewrite.
* [Single-replica read routing](/entities/single-replica-read-routing.md) - After synchronized publication, each fetch or clone is routed to one repository replica rather than coordinated reads across replicas.
* [Slowest-replica consensus latency](/entities/slowest-replica-consensus-latency.md) - Coordinated replication latency is bounded by the slowest participating replica.
* [Spokes repository replication](/entities/spokes-repository-replication.md) - Repository replicas are coordinated through the Spokes architecture to support geographically separated copies.
* [Stale-routing recovery](/entities/stale-routing-recovery.md) - Routing may be stale after failures, and the system restores service by materializing repository state on a newly selected server.
* [Standard-Git GVFS protocol support](/entities/standard-git-gvfs-protocol-support.md) - The GVFS protocol is not incorporated into the standard Git client.
* [Stateless repository placement](/entities/stateless-repository-placement.md) - Any healthy server can materialize repository state without authoritative per-repository placement records.
* [Strict-majority coordinated writes](/entities/strict-majority-coordinated-writes.md) - Uses three replicas, majority-held exclusive locks, strict-majority acceptance, and replica-wide serialization to prevent conflicting divergent writes.
* [System-wide rewrite resource exhaustion](/entities/system-wide-rewrite-resource-exhaustion.md) - Large synchronous repository rewrites can consume CPU and memory and stall the entire client system.
* [Three-phase commit coordination](/entities/three-phase-commit-coordination.md) - Replicas synchronize reference updates through coordinator-directed prepare, commit, and rollback phases.
* [Three-replica repository replication](/entities/three-replica-repository-replication.md) - Each repository maintains a fixed floor of three replicas for consistency, redundancy, and continued push acceptance after one failure.
* [Transactional Git reference updates](/entities/transactional-git-reference-updates.md) - Git reference mutations use atomic, validated transactions that produce deterministic results and roll back completely on failure.
* [Unsynchronized packfile distribution](/entities/unsynchronized-packfile-distribution.md) - Pushed packfiles fan out without consensus because they are unreachable until references commit.
* [Untracked cache](/entities/untracked-cache.md) - Git caches untracked-directory information to reduce large-repository inspection work.
* [Updated large-index file format](/entities/updated-large-index-file-format.md) - An updated index representation reduces I/O and storage for millions of tracked entries.
* [Virtualized filesystem client](/entities/virtualized-filesystem-client.md) - A virtualized filesystem defers populated-size costs to improve large-repository client performance.
* [Working-directory inspection by core commands](/entities/working-directory-inspection-by-core-commands.md) - Core Git commands inspect on-disk working-directory state as part of repository operations.
* [Write unavailability during replication shortfall](/entities/write-unavailability-during-replication-shortfall.md) - Writes become temporarily unavailable when the required replica count cannot be synchronously achieved.
