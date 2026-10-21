# Box supplier agreement extraction

A minimal, runnable sample that turns a supplier agreement stored in Box into
structured procurement data using
[Box AI Extract](https://developer.box.com/guides/box-ai/ai-tutorials/extract-metadata-structured).

It shows the two complex field types that structured extraction supports
beyond scalars: `struct` for grouped vendor details, and `table` for a
repeating delivery schedule. The script calls
`POST /2.0/ai/extract_structured` with the Enhanced Extract Agent, then maps
the response into a flat procurement record you can hand to an ERP,
procurement platform, or project tracker.

This is the companion repository to the tutorial:
**[Turn supplier agreements into structured procurement data with Box AI](https://developer.box.com/tutorials/supplier-agreements)**.

## Why struct and table

| Field type | Returns | Use it for |
| --- | --- | --- |
| `struct` | A single nested JSON object | Related values that belong together, such as a vendor's legal name, address, and contact details |
| `table` | An array of JSON objects sharing one schema | Repeating rows, such as delivery milestones, line items, or payment schedules |

These types mirror how the data is actually used downstream. Instead of
parsing one long vendor block or collapsing a schedule into a single string
after extraction, you map the result directly onto a supplier master record.

Sub-fields accept scalar types only (`string`, `float`, `date`, `enum`,
`multiSelect`). Nesting a `struct` or `table` inside another complex field is
not supported.

> `table` extraction is not limited to visually formatted tables. It picks up
> repeating data whether it appears as a grid, key-value pairs, a form layout,
> or plain prose.

## Project layout

```
box-supplier-agreement-extraction/
├── app.py                          # Runs extraction, maps the procurement record
├── box_client.py                   # CCG Service Account auth
├── extract.py                      # Box AI structured extract call
├── schema.py                       # struct + table field definitions
├── sample-supplier-agreement.pdf   # Test document to upload to Box
├── requirements.txt
├── .env.example
└── .gitignore
```

## Prerequisites

- **Python 3.11+**
- A [free Box developer account](https://account.box.com/signup/developer),
  or a [Box Enterprise account](https://www.box.com/pricing) with **Box AI**
  enabled. Consumer/Individual accounts do not work.
- A **Client Credentials Grant (CCG)** Platform App, **authorized** in the
  Admin Console, with these scopes enabled:
  - **Read and write all files and folders stored in Box**
  - **Manage AI**
- A supplier agreement uploaded to Box, in a folder the app's **Service
  Account** can access

## Setup

1. **Clone and enter the project**

   ```bash
   git clone https://github.com/box-community/box-supplier-agreement-extraction.git
   cd box-supplier-agreement-extraction
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   Re-activate the venv (`source .venv/bin/activate`) in every new terminal
   tab. A `ModuleNotFoundError` almost always means it is not active.

3. **Upload the agreement to Box.** Use the included
   `sample-supplier-agreement.pdf`, or your own document. Note the **file ID**
   from the URL (`https://app.box.com/file/123456789` > `123456789`).

   **Critical:** invite the app's Service Account as a collaborator on the
   folder that holds the file. Find the Service Account email in Developer
   Console > your app > **General Settings** > **Service Account ID** (it looks
   like `AutomationUser_xxxxx_xxxxxx@boxdevedition.com`). Without this
   collaboration, API calls return `404 Not Found`.

4. **Configure credentials**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and fill in:

   - `BOX_CLIENT_ID`, `BOX_CLIENT_SECRET`, `BOX_ENTERPRISE_ID` from the
     Developer Console
   - `AGREEMENT_FILE_ID` from step 3

   > **Never commit `.env`.** It is already in `.gitignore`.

## Run

```bash
python app.py
```

The script prints the raw extraction, then the mapped procurement record.
Output looks similar to this:

```json
{
  "agreement_effective_date": "2026-06-01",
  "payment_terms": "Net 45",
  "vendor": {
    "legal_name": "Nexus Industrial Solutions Ltd.",
    "address": "47 Canary Wharf, Level 12, London, E14 5AB",
    "country": "United Kingdom",
    "contact_person": "Oliver Hartmann",
    "email": "o.hartmann@nexusindustrial.co.uk",
    "phone": "+44 20 7946 0832"
  },
  "delivery_schedule": [
    {
      "phase": "Phase 1 - Infrastructure",
      "items": "Server Racks (qty 6), UPS (qty 3)",
      "delivery_date": "2026-07-15",
      "destination": "Chicago, IL",
      "status": "Scheduled"
    },
    {
      "phase": "Phase 2 - Networking",
      "items": "48-Port Switches (all), Fibre Cables (all)",
      "delivery_date": "2026-08-01",
      "destination": "Chicago, IL",
      "status": "Scheduled"
    }
  ]
}
```

## How it works

1. `box_client.py` authenticates as the app's Service Account with CCG.
2. `schema.py` defines the fields to pull, including the `vendor` struct and
   the `delivery_schedule` table.
3. `extract.py` sends that schema to `POST /2.0/ai/extract_structured`,
   referencing the Enhanced Extract Agent by ID (`enhanced_extract_agent`).
   The agent is predefined, so there is nothing to create or configure.
4. `app.py` flattens the nested response into a procurement record.

## Adapt it

- **Change the schema.** Edit `EXTRACTION_FIELDS` in `schema.py`. Add a
  field-level `prompt` to any field whose meaning is ambiguous in your
  documents - it is the single biggest accuracy lever.
- **Write results back to Box.** Attach the flattened top-level values as a
  metadata instance so agreements become searchable with
  [metadata queries](https://developer.box.com/guides/metadata/queries). See
  [box-automate-invoice-intake](https://github.com/box-community/box-automate-invoice-intake)
  for an end-to-end write-back pattern.
- **Trigger it automatically.** Register a webhook on the agreements folder so
  each upload runs extraction, and
  [verify webhook signatures](https://developer.box.com/guides/webhooks/v2/signatures-v2)
  in production.
- **Reuse one schema across many documents.** Define the fields in a
  [metadata template](https://developer.box.com/guides/box-ai/ai-tutorials/extract-metadata-structured#use-metadata-template)
  instead of inline.

## Security notes

- Keep the client secret, enterprise ID, and access tokens server-side.
- Grant the Service Account only the folder access it needs.
- Treat extracted values as untrusted input before writing them to downstream
  systems.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `ModuleNotFoundError` | Activate the venv: `source .venv/bin/activate`. Install `boxsdk` only; it provides the `box_sdk_gen` module. Don't also install `box-sdk-gen`. |
| `invalid_client` | Check `BOX_CLIENT_ID` / `BOX_CLIENT_SECRET` / `BOX_ENTERPRISE_ID` in `.env`. |
| `unauthorized_client` | Authorize the app in the Admin Console (Developer Console > Authorization > Review and Submit). |
| `404 Not Found` | Invite the Service Account as a collaborator on the folder containing the agreement. |
| Sub-field values empty or merged | Confirm sub-fields use scalar types only, that each complex field has a `fields` array, and add a `prompt` to clarify what to extract. |
| Extraction fails / AI errors | Confirm the **Manage AI** scope is enabled and the app was re-authorized after enabling it. Box AI must be available on the account. |

## License

[MIT](./LICENSE)
