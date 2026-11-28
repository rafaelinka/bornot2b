# Peppol: selected identifier-rule experiment, November 28, 2026

This experiment executes the unmodified XPath expressions of **PEPPOL-COMMON-R040** (GLN13) and **PEPPOL-COMMON-R054** (Dutch KVK format), together with the upstream `u:gln` function, extracted from the November 2026 Peppol Schematron. It uses SaxonC-HE as the XSLT processor and lxml to extract the assertions and construct the test harness. The harness is editorial code, not an OpenPeppol validator.

All five XML fixtures are synthetic fragments. The strings are deliberately chosen test values and do not assert that an organization is registered. Each fixture contains one identifier under each tested scheme. They are **not complete, conformant UBL invoices or credit notes**. Only two selected assertions are executed; no claim is made about all BIS rules, XSD conformance, network delivery, a provider, an ERP, Invoice Response implementation or a payment.

## Reproduce

Install the pinned dependencies into a virtual environment and run:

```sh
python run_selected_rules.py
```

Alternatively pass `--schematron /absolute/path/PEPPOL-EN16931-UBL.sch`. The runner verifies the recorded SHA-256 before executing either rule; it stops if upstream bytes change. The full upstream Schematron is not vendored here. `results.json` records the source URL, exact hash, release marker, processor version, rule expressions, fixture hashes and observed results.

The official source is [OpenPeppol's November 2026 Schematron](https://docs.peppol.eu/poacc/billing/3.0/2026-Q4/files/PEPPOL-EN16931-UBL.sch). Its header states that the CEN/EN16931-1 terms are reproduced with CEN permission and disclaims CEN liability and warranties. The runner retrieves the source as published; this repository does not grant additional rights to it. The short expressions and test results identify the precise experiment rather than redistribute the full specification.

The documentation date was checked independently on November 28, 2026. Both the [Billing release notes](https://docs.peppol.eu/poacc/billing/3.0/2026-Q4/release-notes/) and [other BIS release notes](https://docs.peppol.eu/poacc/upgrade-3/2026-Q4/release-notes/) state publication on November 23, 2026 and mandatory use from February 22, 2027. A search-engine copy is not treated as the controlling date.
