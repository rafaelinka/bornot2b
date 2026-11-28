#!/usr/bin/env python3
"""Execute two unmodified November 2026 Peppol rule expressions.

This is a selected-rule experiment, not UBL/XSD or full BIS validation.
The upstream Schematron and u:gln function are downloaded or read locally;
their contents must match the checksum recorded on November 28, 2026.
"""
from pathlib import Path
from copy import deepcopy
import argparse
import hashlib
import json
import platform
import tempfile
import urllib.request

from lxml import etree
from saxonche import PySaxonProcessor

SOURCE_URL = 'https://docs.peppol.eu/poacc/billing/3.0/2026-Q4/files/PEPPOL-EN16931-UBL.sch'
EXPECTED_SHA256 = '6436303f7a2c1a4bf5eddd5c89fb0c60e2d563cd725f2ab12b2fd5ad98680ad6'
RULE_IDS = ('PEPPOL-COMMON-R040', 'PEPPOL-COMMON-R054')
SCH = 'http://purl.oclc.org/dsdl/schematron'
XSL = 'http://www.w3.org/1999/XSL/Transform'
CBC = 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2'
CAC = 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2'
BASE = Path(__file__).resolve().parent


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--schematron', type=Path, help='Use a local copy with the pinned hash')
    parser.add_argument('--output', type=Path, default=BASE / 'results.json')
    args = parser.parse_args()
    if args.schematron:
        source = args.schematron.read_bytes()
    else:
        with urllib.request.urlopen(SOURCE_URL, timeout=30) as response:
            source = response.read()
    digest = hashlib.sha256(source).hexdigest()
    if digest != EXPECTED_SHA256:
        raise SystemExit(f'Upstream Schematron changed: {digest}; review before rerunning')
    schema = etree.fromstring(source, parser=etree.XMLParser(resolve_entities=False, no_network=True))
    sheet = etree.Element(f'{{{XSL}}}stylesheet', version='2.0', nsmap={
        'xsl': XSL, 'cbc': CBC, 'cac': CAC,
        'xs': 'http://www.w3.org/2001/XMLSchema', 'u': 'utils',
    })
    etree.SubElement(sheet, f'{{{XSL}}}output', method='xml', indent='yes')
    # Copy the official checksum function without rewriting its calculation.
    function = schema.xpath('xsl:function[@name="u:gln"]', namespaces={'xsl': XSL})
    assert len(function) == 1
    sheet.append(deepcopy(function[0]))
    root_template = etree.SubElement(sheet, f'{{{XSL}}}template', match='/')
    result_node = etree.SubElement(root_template, 'results')
    rules = []
    for i, rule_id in enumerate(RULE_IDS):
        assertion = schema.xpath('sch:pattern/sch:rule/sch:assert[@id=$id]',
                                 namespaces={'sch': SCH}, id=rule_id)
        assert len(assertion) == 1, rule_id
        assertion = assertion[0]
        context, expression, severity = (assertion.getparent().get('context'),
                                         assertion.get('test'), assertion.get('flag'))
        mode = f'rule_{i}'
        etree.SubElement(result_node, f'{{{XSL}}}apply-templates', select='//*', mode=mode)
        etree.SubElement(sheet, f'{{{XSL}}}template', match='@*|node()', mode=mode, priority='-10')
        template = etree.SubElement(sheet, f'{{{XSL}}}template', match=context, mode=mode)
        check = etree.SubElement(template, 'check', rule=rule_id, severity=severity)
        etree.SubElement(check, f'{{{XSL}}}attribute', name='value', select='normalize-space()')
        etree.SubElement(check, f'{{{XSL}}}attribute', name='passed', select=f'boolean({expression})')
        if rule_id == 'PEPPOL-COMMON-R040':
            etree.SubElement(check, f'{{{XSL}}}attribute', name='checksum_only',
                             select='u:gln(normalize-space())')
        rules.append({'id': rule_id, 'context': context, 'test': expression, 'severity': severity})
    with PySaxonProcessor(license=False) as processor, tempfile.TemporaryDirectory() as scratch:
        stylesheet = Path(scratch) / 'selected-rules.xsl'
        stylesheet.write_bytes(etree.tostring(sheet, xml_declaration=True, encoding='utf-8'))
        executable = processor.new_xslt30_processor().compile_stylesheet(stylesheet_file=str(stylesheet))
        cases = []
        expected = {
            'invoice-valid-identifiers.xml': [],
            'invoice-gln-bad-check-digit.xml': ['PEPPOL-COMMON-R040'],
            'invoice-gln-too-long.xml': ['PEPPOL-COMMON-R040'],
            'invoice-kvk-too-short.xml': ['PEPPOL-COMMON-R054'],
            'creditnote-valid-identifiers.xml': [],
        }
        for filename, expected_failures in expected.items():
            fixture = BASE / 'fixtures' / filename
            output = executable.transform_to_string(source_file=str(fixture))
            checks = [dict(node.attrib) for node in etree.fromstring(output.encode()).findall('check')]
            assert len(checks) == 2, (filename, checks)
            failures = [c['rule'] for c in checks if c['passed'] == 'false']
            assert failures == expected_failures, (filename, failures, expected_failures)
            cases.append({'fixture': filename, 'sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
                          'checks': checks, 'failed_rules': failures})
        report = {
            'checked_on': '2026-11-28', 'source_url': SOURCE_URL, 'source_sha256': digest,
            'source_bytes': len(source), 'source_release': '2026 November 3.1.0',
            'engine': processor.version, 'python': platform.python_version(),
            'scope': 'Only two selected identifier assertions; synthetic XML fragments, not complete conformant invoices.',
            'not_tested': ['UBL/XSD schema', 'all other BIS rules', 'directory registration',
                           'Invoice Response processing', 'transport or access point', 'ERP', 'bank settlement'],
            'rules': rules, 'cases': cases, 'assertions_evaluated': sum(len(c['checks']) for c in cases),
        }
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'cases': len(cases), 'assertions_evaluated': report['assertions_evaluated'],
                      'expected_failures_observed': 3, 'output': str(args.output)}))


if __name__ == '__main__':
    run()
