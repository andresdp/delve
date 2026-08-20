# Concepts

Shared domain vocabulary for this project — entities, named processes, and status concepts with project-specific meaning. Seeded with core domain vocabulary, then accretes as ce-compound and ce-compound-refresh process learnings; direct edits are fine. Glossary only, not a spec or catch-all.

## Relationships

A Taxonomy accumulates Iterations as it grows. Each Iteration holds a set of Dimensions; each Dimension owns its own Values and links to other Dimensions through Relations. Selected Dimensions is a filtered view drawn from one Iteration's Dimensions, kept alongside — never replacing — the full history. A Grounded Theory Report renders one chosen view (a specific Iteration, Selected Dimensions, or the latest Iteration) and includes at most one Narrative Summary. A Seeded Taxonomy is a saved Taxonomy's final (or only) Iteration loaded as the starting point of a new run: Train Mode refines it further, while Test Mode freezes its Dimensions and only allows Values to grow.

## Taxonomy

The evolving structure a corpus is organized into: a set of Dimensions, each with its Values and Relations to other Dimensions. Built up across multiple Iterations rather than produced in one pass.

## Iteration

One snapshot of the Taxonomy's Dimensions captured at a specific point in its generation history (after an update, a review, or a consolidation pass). Later processing (a Grounded Theory Report, classification) always renders one specific Iteration or view — never an ambiguous blend of several.

## Dimension

An axis of variation the Taxonomy captures — documents differ along a Dimension's axis, and a well-formed Dimension is orthogonal to every other Dimension (it captures a distinct *type* of distinction, not a value dressed up as an axis).

## Value

A specific point or decision along one Dimension's axis, distinct from the Dimension itself. A Value is supported by the documents whose Open Coding results led to it.

## Relation

A typed, directed link from one Dimension to another, describing how the two interact rather than incidental co-occurrence. Types: `precondition`, `consequence`, `co_occurring`, `constrains`.

## Open Coding

The per-document, fine-grained concept-extraction step that runs before a batch of documents is folded into the Taxonomy's Dimensions. Each document's Open Coding output is what a later Value's supporting evidence traces back to.

## Saturation

The condition under which the Taxonomy stops growing from new document batches: reached when a configured streak of batches in a row add no concept not already covered by an existing Dimension. Reaching Saturation (or exhausting all batches) ends the open-coding/update cycle and moves the Taxonomy into review.

## Selected Dimensions

The use-case-relevant subset of an Iteration's Dimensions, chosen by a dedicated selection step and dropped-with-rationale rather than silently deleted. The full Dimension history is preserved alongside Selected Dimensions, never replaced by it — code that reads "the current view" must be explicit about which of the two it means. A reader of a Grounded Theory Report sees the drop rationale directly, in its Discarded Dimensions section.

## Grounded Theory Report

A self-contained markdown document rendering one Taxonomy view (a specific Iteration, Selected Dimensions, or the latest Iteration) for a reader who never ran the pipeline: a Narrative Summary, a relationship diagram of Dimensions and their Relations, a catalog of each Dimension's Values, and — whenever the pipeline recorded at least one dimension the selection step excluded — a Discarded Dimensions section naming each and why. Everything except the Narrative Summary is rendered verbatim from the Taxonomy data — never reworded by a model.

## Train Mode

The run mode in which the Taxonomy — seeded from a saved Taxonomy or built from scratch — is refined through the open-coding → update → saturation loop. The existing default mode; a run with no Taxonomy input behaves exactly as before.

## Test Mode

The run mode in which a Seeded Taxonomy's Dimensions are frozen: no dimension is added, renamed, merged, split, or dropped. New documents are classified into existing Dimensions; a document that fits no Dimension goes to the predefined fallback category ("Other"), and a document whose decision matches no existing Value may append a new Value to its Dimension, recording the triggering documents as supporting evidence.

## Seeded Taxonomy

The final (or only) Iteration of a saved Taxonomy JSON, loaded as the starting Taxonomy of a new run. In Train Mode it is the basis for further refinement; in Test Mode it is the frozen classification framework.

## Delta Summary

The test-mode output that reports what changed relative to the Seeded Taxonomy: the new Values appended per Dimension, and the list of documents that landed in the fallback bucket.

## Narrative Summary

The one prose section of a Grounded Theory Report that a model is allowed to polish for readability. It may only reword or synthesize text that already exists elsewhere in the rendered view (an Iteration's stored rationale, the in-scope Dimensions' descriptions) — it must never introduce a Dimension, Relation, or Value absent from that view. It must also state the use case the report serves, plainly and up front, whenever the rendered view doesn't already make that clear on its own.
