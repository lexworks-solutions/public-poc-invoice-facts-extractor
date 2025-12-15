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
  - Source: [Xero](https://www.xero.com/us/)'s "Very Orange" invoice template
- `invoice-example-2.pdf`: Standard invoice, but has a different layout from the others. All information is in the first page.
  - Source: [Sliced Invoices](https://slicedinvoices.com)
- `invoice-example-3.pdf`: Not a standard invoice, has some styling and is multiple pages long. The file is also significantly bigger - 1.6 MB, while others are 90.1 KiB or 42.6 KiB.
  - Invoice source: [Adobe Express](https://new.express.adobe.com/design/template/urn:aaid:sc:VA6C2:2321d6eb-e904-57f1-874c-df910c3f9490?category=templates&referrer=https%3A%2F%2Fwww.google.com%2F&url=%2Fexpress%2Ftemplates%2Finvoice&placement=template-x&locale=en-US&contentRegion=us)

After executing the tests, we have found that:

1. The workflow is viable and the AI is able to reliably extract information from the invoices.
2. Using TSV is likely unnecessary with the recent development of multimodal models. Uploading the invoices directly could lead to reduced token usage and potentially more accuracy.

**Note:** This project was built as a showcase of the processes I used to solve a similar problem in 2023, when multimodal models were not as accurate as today. For anyone looking to build a similar solution, I advise using one of today's out-of-the-box options, such as AWS Textract, rather than attempting to process the TSVs. The current stack is still convenient though, since it's free.
