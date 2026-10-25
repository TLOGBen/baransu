# documents — a hypothesis whose source is a document

A document that states how a process must run — a spec, an SOP, a contract — is a source like code. Two documents, or a document and code, compared ("does A satisfy B") are one hypothesis: B's rules, A's model.

## What one step is

A step is one action the document gives to one actor, which the document says is complete before anyone else can observe it. Where the document says nothing about what happens between two actions, they are separate steps, and other actors may act between them. Where it leaves the order of two actions open, the model allows both orders.

## Readings

Wording that allows more than one meaning becomes a question naming who can answer it. Model a second reading only when it changes some rule's verdict: run each such reading and report each verdict under the question. A reading that changes no verdict is noted in one line and not modelled. This keeps the number of readings to the ones that matter.

## Every rule carries its quote

Each rule quotes the passage it comes from, with its location. A contradiction is two quotes that cannot both hold, shown by a trace; a gap is a situation the model reaches that no passage covers; an ambiguity is a question. The report counts each kind.
