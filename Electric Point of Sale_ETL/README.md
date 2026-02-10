# EPOS Data Pipeline — README

This script automates the intake, validation, cleaning, enrichment, and archival of EPOS CSV files. It is designed to:

- Pick up raw CSV files from a **data dump** folder.
- Perform **schema checks** and **data-quality validations**.
- Apply **normalisation and business rules** using functions from `epos_functions`.
- Save a **cleaned, dated CSV** into a customer/year folder hierarchy.
- **Stream** the cleaned data to a downstream destination.
- Remove the original raw file after successful processing.

> **Why this approach?** It enforces consistent data types, standardises text fields, and guarantees that saved outputs are versioned by date and organised by customer and year—reducing manual effort and ensuring repeatability.

---

## Prerequisites

- **Python 3.9+** (recommended)
- Packages:
  - `pandas`
  - `python-dotenv`
- A local module named **`epos_functions.py`** on the Python path (same folder or installable package) exposing the functions referenced in this script.

Install dependencies:

```bash
pip install pandas python-dotenv
```
