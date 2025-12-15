# Roadmap

## Phase 1: Proof of Concept

Before committing time to the core business idea, we'll derisk the implementation by verifying what is the minimum required setup for processing invoices as a proof of concept.

In order to do this, we'll perform the following:

1. Acquire invoices for our testing with at least 3 distinct formats.
2. Define a basic format for the extracted information.
3. Define the minimum Synthesis Categories, such as price, due date and line items.
4. Create the minimum required code to extract text from the local invoice files and pass them on for Synthesis.
5. Iterate on the training dataset, AI prompts and models, stack and/or code until we are able to either verify processing happening as expected or impossibility of doing so.

For the example invoices:

- `invoice-example-1.pdf`: Standard invoice, exported from Xero's Demo Organisation. Has information in the 2nd page.
- `invoice-example-2.pdf`: Standard invoice, but has a different layout from the others. All information is in the first page.
- `invoice-example-3.pdf`: Not a standard invoice, has some styling and is multiple pages long. The file is also significantly bigger - 1.6 MB, while others are 90.1 KiB or 42.6 KiB.
