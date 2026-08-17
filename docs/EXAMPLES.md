# Delve — Usage Examples

## Example: Product Reviews Taxonomy

This example uses the included `examples/product_reviews.json` corpus containing 20 laptop product reviews.

### Command

```bash
python main.py --corpus examples/product_reviews.json --quiet --output output/
```

### Console Output

The `--quiet` flag suppresses logging and shows only the rich-formatted pipeline progress and results.

#### 1. Corpus Loading

```
╭──────────────────── 📂 Loading Corpus ────────────────────╮
│ File: examples/product_reviews.json                       │
│ Documents: 20                                             │
╰───────────────────────────────────────────────────────────╯
```

#### 2. Pipeline Configuration

```
╭──────────────────────── 🚀 Delve ─────────────────────────╮
│ Starting taxonomy generation pipeline...                  │
│                                                           │
│ Taxonomy: taxonomy                                        │
│ Model: openai/gpt-5.4-nano                                │
│ Fast LLM: openai/gpt-5.4-nano                             │
╰───────────────────────────────────────────────────────────╯
```

#### 3. Step-by-Step Progress

Each pipeline node is displayed in real-time as it executes:

```
  📂 Loading corpus  ✓
  📝 Generating summaries  ✓
  📦 Creating minibatches  ✓
  🧠 Generating initial taxonomy (minibatch 1/2)  ✓
  🔄 Updating taxonomy (minibatch 2/2)  ✓
  🔍 Reviewing taxonomy  ✓
  🏷️ Labeling documents  ✓

  ⏱️  Pipeline completed in 20.7s  ·  🪙 33,216 tokens (29,087 prompt + 4,129 completion)
```

#### 4. Generated Taxonomy

The taxonomy table shows the final categories with their descriptions:

```
                  📊 Generated Taxonomy: taxonomy
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃    # ┃ Name                    ┃ Description
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━
│    1 │ Device portability and  │ Complaints about weight an
│      │ carrying comfort        │ all-day commuting comfort;
│      │                         │ inconvenient for extended
│      │                         │ carrying despite desk use.
├──────┼─────────────────────────┼───────────────────────────
│    2 │ Battery life while in   │ Battery duration during
│      │ everyday use            │ continuous typical tasks;
│      │                         │ whether real runtime meets
│      │                         │ expectations.
├──────┼─────────────────────────┼───────────────────────────
│    3 │ Thermal noise and fan   │ Annoying fan/PC noise and
│      │ behavior                │ whirring during light task
│      │                         │ acoustic discomfort from
│      │                         │ cooling systems.
├──────┼─────────────────────────┼───────────────────────────
│    4 │ Display flickering and  │ Screen flicker at low
│      │ low-brightness          │ brightness and poor nightt
│      │ usability               │ usability prompting return
├──────┼─────────────────────────┼───────────────────────────
│    5 │ Video-call camera color │ Video-call camera color is
│      │ accuracy                │ (washed-out, inaccurate to
│      │                         │ versus expectations or pri
│      │                         │ devices.
├──────┼─────────────────────────┼───────────────────────────
│    6 │ Software setup and      │ Discouraging initial setup
│      │ antivirus upgrade       │ recurring antivirus upgrad
│      │ prompts                 │ notifications disrupting u
│      │                         │ experience.
├──────┼─────────────────────────┼───────────────────────────
│    7 │ Built-in speaker audio  │ Assessment of laptop speak
│      │ quality                 │ clarity, bass, loudness, a
│      │                         │ overall listening quality.
├──────┼─────────────────────────┼───────────────────────────
│    8 │ Laptop hardware         │ Failures or instability:
│      │ reliability and         │ trackpad, Wi‑Fi disconnect
│      │ connectivity            │ hinge looseness, wobble, o
│      │                         │ similar connectivity issue
└──────┴─────────────────────────┴───────────────────────────┘
  Total categories: 8  ·  Iterations: 3
```

#### 5. Taxonomy Rationale

The rationale panel shows the LLM's reasoning for each taxonomy iteration:

```
╭────────────────── 💬 Taxonomy Rationale ──────────────────╮
│ 1. Generation: Grouped by distinct device-review intents  │
│ (weight, battery, noise, display, camera, setup,          │
│ speakers) and separate software/workflow performance; no  │
│ user feedback provided.                                   │
│                                                           │
│ 2. Update: I refined the taxonomy to cover all new themes │
│ while staying at 8 categories. Added hardware             │
│ reliability/connectivity as a dedicated cluster...        │
│                                                           │
│ 3. Review: Coverage is complete for the provided themes   │
│ (Wi‑Fi/hinge/connectivity, audio, display, battery,       │
│ noise, camera, antivirus/setup, portability). Categories  │
│ are distinct with minimal overlap.                        │
╰───────────────────────────────────────────────────────────╯
```

#### 6. Document Labeling Results

Each document is classified with a category and confidence score:

```
                         📄 Document Labeling Results
┏━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━
┃ Category                ┃ Score  ┃ Document Preview
┡━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━
│ Battery life while in   │  0.98  │ The battery life on this
│ everyday use            │        │ incredible. I got 12 hou...
│ Display flickering and  │  1.00  │ Screen flickers randomly
│ low-brightness          │        │ is below 30%. Very annoy...
│ Other                   │  0.05  │ Keyboard feels premium w...
│ Software setup and      │  0.95  │ Setup was straightforwar
│ antivirus upgrade       │        │ pre-installed antivirus...
│ Laptop hardware         │  0.95  │ The trackpad is unrespon
│ reliability and         │        │ top-left corner...
│ connectivity            │        │
│ Thermal noise and fan   │  0.98  │ Fan noise is unacceptabl...
│ behavior                │        │
│ ...                     │  ...   │ ...
└─────────────────────────┴────────┴─────────────────────────┘
```

#### 7. Taxonomy Tree

A tree view shows categories with their classified documents:

```
📂 taxonomy  (8 categories, 20 documents)
├── Device portability and carrying comfort (3 docs)
│   ├── 📄 Lightweight and portable. Fits perfectly... (0.90)
│   ├── 📄 Perfect for students. Handles note-taking... (0.05)
│   └── 📄 It's way too heavy to carry around all day... (1.00)
├── Battery life while in everyday use (3 docs)
│   ├── 📄 The battery life on this laptop is incredible... (0.98)
│   ├── 📄 USB-C charging is a game changer... (0.10)
│   └── 📄 Rendering 4K video in Premiere Pro is smooth... (0.20)
├── Thermal noise and fan behavior (2 docs)
│   ├── 📄 Fan noise is unacceptable... (0.98)
│   └── 📄 Gets extremely hot during extended gaming... (0.70)
├── Display flickering and low-brightness usability (2 docs)
│   ├── 📄 Screen flickers randomly when brightness... (1.00)
│   └── 📄 Display colours are vibrant and the 1440p... (0.40)
├── Video-call camera color accuracy (2 docs)
│   ├── 📄 Camera quality for video calls is decent... (0.90)
│   └── 📄 The colour calibration out of the box... (0.20)
├── Software setup and antivirus upgrade prompts (1 docs)
│   └── 📄 Setup was straightforward but the pre-installed... (0.95)
├── Built-in speaker audio quality (1 docs)
│   └── 📄 Speakers are surprisingly good for a laptop... (0.98)
├── Laptop hardware reliability and connectivity (3 docs)
│   ├── 📄 The trackpad is unresponsive in the top-left... (0.95)
│   ├── 📄 The hinge feels loose after just 3 months... (0.95)
│   └── 📄 Wifi keeps disconnecting from my home network... (0.95)
└── Other (3 docs)
    ├── 📄 Keyboard feels premium with great key travel... (0.05)
    ├── 📄 This thing is fast. Compiles my React projects... (0.10)
    └── 📄 Storage expansion was easy with the second NVMe... (—)
```

#### 8. Output Files

Four timestamped JSON files are saved to the output folder:

```
╭──────────────────── 💾 Results Saved ─────────────────────╮
│ Documents:      output/documents_20260607_175157.json     │
│ Taxonomy:       output/taxonomy_20260607_175157.json      │
│ Messages:        output/messages_20260607_175157.json     │
│ Clusters:       output/clusters_20260607_175157.json      │
╰───────────────────────────────────────────────────────────╯

✅ Done.
```

---

## Example: Software Architecture Decisions

This example uses a corpus of 26 software architecture design decisions from a delivery management system (`examples/decisions_results.json`).

### 1. Prepare the Corpus

The source JSON has structured decision objects. First, flatten them into a corpus file:

```bash
python examples/prepare_decisions_corpus.py
```

This generates `examples/architecture_decisions.json` — a flat JSON array where each entry combines the decision's description, pattern name (in parentheses), and rationale into a single string.

### 2. Configure the Use Case

A domain-specific config file (`examples/config_decisions.yaml`) sets the `use_case` to guide taxonomy generation toward architecture patterns:

```yaml
taxonomy:
  name: "architecture-decisions"
  max_num_clusters: 6
  use_case: >-
    Classify software architecture design decisions for a food delivery
    company migrating from a monolithic system to microservices. The
    system serves PC and mobile clients accessing customer and order data
    via SQL databases, with business modules for Customers (critical),
    Orders (non-critical, with retry limits), Delivery & Routing
    (critical, with optimization algorithms based on truck delay),
    Statistics (non-critical, order/truck status), Incidents
    (semi-critical, route manager alerts), and external Payments
    (critical, third-party gateway). An OrderManager mediates between
    customers, orders, delivery, and incidents. Group decisions by their
    architectural pattern (e.g., API Gateway, Microservices, Adapter,
    Strategy, Repository), the functional module they address, and their
    integration or resilience strategy.
```

### 3. Run the Pipeline

```bash
python main.py --corpus examples/architecture_decisions.json --config examples/config_decisions.yaml --quiet --output output/
```

### Console Output

#### Step-by-Step Progress

```
  📂 Loading corpus  ✓
  📝 Generating summaries  ✓
  📦 Creating minibatches  ✓
  🧠 Generating initial taxonomy (minibatch 1/3)  ✓
  🔄 Updating taxonomy (minibatch 2/3)  ✓
  🔄 Updating taxonomy (minibatch 3/3)  ✓
  🔍 Reviewing taxonomy  ✓
  🏷️ Labeling documents  ✓

  ⏱️  Pipeline completed in 38.9s  ·  🪙 47,276 tokens (41,849 prompt + 5,427 completion)
```

#### Generated Taxonomy

```
                        📊 Generated Taxonomy: architecture-decisions
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃    # ┃ Name                                     ┃ Description                             ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│    1 │ API gateway routing for client and       │ Centralizes entry/routing for HTTP/REST │
│      │ services                                 │ client requests to backend              │
│      │                                          │ microservices and client/mobile access. │
│    2 │ Runtime selection of optimization        │ Delivery selects among multiple         │
│      │ strategy classes                         │ optimization algorithms at runtime.     │
│    3 │ Microkernel plugin loading for           │ Optimization algorithms are plugins     │
│      │ optimization algorithms                  │ loaded into a microkernel core.         │
│    4 │ Circuit breaker for failure-cascade      │ Prevents cascading failures by blocking │
│      │ resilience                               │ dependent-call cascades.                │
│    5 │ Bulkhead isolation without limiting      │ Isolates components; explicitly avoids  │
│      │ client retries                           │ throttling for client order retries.    │
│    6 │ Microservices CRUD for customers and     │ Customer and order service boundaries   │
│      │ orders                                   │ and REST CRUD APIs.                     │
│    7 │ Service decomposition for statistics,    │ Splits statistics, incident handling,   │
│      │ incidents, routing                       │ and routing into distinct microservices.│
│    8 │ Facade and adapter for payments client   │ Simplified internal interface for       │
│      │ interface                                │ payments, unifying external access.     │
│    9 │ Repository-per-service SQL persistence   │ Each microservice owns its SQL          │
│      │ ownership                                │ persistence via dedicated repositories. │
│   10 │ Observer events and incident event       │ Observer-based state-change events and  │
│      │ sourcing                                 │ event sourcing for incident histories.  │
└──────┴──────────────────────────────────────────┴─────────────────────────────────────────┘
  Total categories: 10  ·  Iterations: 4
```

#### Taxonomy Tree (excerpt)

```
📂 architecture-decisions  (10 categories, 26 documents)
├── API gateway routing for client and services (9 docs)
│   ├── 📄 Use the Gateway to route requests to the appropriate services... (0.95)
│   ├── 📄 Deploy an API Gateway to expose and manage APIs for accessing... (0.95)
│   └── ... and 7 more
├── Runtime selection of optimization strategy classes (1 docs)
│   └── 📄 Implement two optimization algorithms as separate strategy classes... (0.95)
├── Facade and adapter for payments client interface (3 docs)
│   ├── 📄 Implement an Adapter module that wraps the external Payments... (0.95)
│   └── ... and 2 more
├── Observer events and incident event sourcing (2 docs)
│   ├── 📄 Use observer pattern internally within microservices... (0.90)
│   └── 📄 Adopt event sourcing for critical modules like incidents... (0.95)
└── ...
```

#### Output Files

The taxonomy name (`architecture-decisions`) is used as a prefix in all output filenames:

```
╭──────────────────── 💾 Results Saved ─────────────────────╮
│ Documents:      output/architecture-decisions_documents_20260608_230906.json
│ Taxonomy:       output/architecture-decisions_taxonomy_20260608_230906.json
│ Messages:        output/architecture-decisions_messages_20260608_230906.json
│ Clusters:       output/architecture-decisions_clusters_20260608_230906.json
╰───────────────────────────────────────────────────────────╯
```

---

## More Examples

### Custom Taxonomy Name

```bash
python main.py --corpus examples/product_reviews.json --name "Laptop Reviews" --quiet --output output/
```

### Using a Different Model

```bash
python main.py --corpus examples/customer_support.txt --model groq/llama-3.3-70b-versatile --quiet
```

### Verbose Mode (with Logging)

Without `--quiet`, detailed logging is shown alongside the rich output:

```bash
python main.py --corpus examples/product_reviews.json --output output/
```
