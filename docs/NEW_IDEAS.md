* The taxonomy generation process should allow to start from an existing taxonomy, and run the whole Langgraph graph starting from that basis. Optionally, there can be some user feedback to take into account in the process.

* The taxonomy process can be run in 2 modes: i) train, which is the current mode in which the taxonomy is progressively built and updated; and ii) test, in which the existing taxonomy is not modified, but new batches of documents can be added to the existing dimensions. 

* Since the taxonomy generation process indirectly produced a grounded theory (through open coding, selective coding, etc), it should be able to generate a markdown respresentation of this theory, including a mermaid chart showing the main concepts and relationships of the theory. 

* It should be aable to run the same generation process multiple times (for the same inputs) so as to assess the consistency and robustness of the generated taxonomy.

* Currently, when generating and reviewing a current snapshot of the taxonomy, the prompts specify several quality criteria to be considered/checked by the LLM. These criteria should be implemented as separate llm-as-a-judge metrics, for instance, using GEval from the Deepeval library, to get a scoreboard. Furthermore, once a taxonomy is available, it should be possible to execute these criteria in a standalone mode to get a scoreboard. https://deepeval.com/docs/metrics-llm-evals

* Check the differences (and potential similarities) between the saturation and review nodes. Would it be possible to have a feedback loop (return arc) in the review node?

* An alternative strategy for checking the taxonomy, once the dimensions and values are provided, is to sample points (i.e., solutions) in the space that combine more than one value across the dimensions. These alternative solutions could be checked for consistency, diversity or other properties.