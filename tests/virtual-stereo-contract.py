#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'protocols'


class VirtualStereoContract(unittest.TestCase):
    def test_device(self):
        protocol = ET.parse(ROOT / 'kde-output-device-v2.xml')
        for name in ('kde_output_device_registry_v2', 'kde_output_device_v2', 'kde_output_device_mode_v2'):
            self.assertEqual(protocol.find(f"interface[@name='{name}']").get('version'), '24')
        capability = protocol.find("interface[@name='kde_output_device_v2']/enum[@name='capability']/entry[@name='virtual_stereo']")
        self.assertEqual(int(capability.get('value'), 0), 0x20000)
        self.assertEqual(capability.get('since'), '24')
        event = protocol.find("interface[@name='kde_output_device_v2']/event[@name='stereo_formats']")
        self.assertEqual(event.get('since'), '24')
        self.assertEqual([(a.get('name'), a.get('type')) for a in event.findall('arg')], [('anaglyph', 'uint'), ('other_stereo_formats', 'uint')])
        entries = protocol.findall("interface[@name='kde_output_device_mode_v2']/enum[@name='flags']/entry")
        values = {entry.get('name'): int(entry.get('value'), 0) for entry in entries}
        expected = {'custom': 1, 'reduced_blanking': 2, 'stereo_side_by_side_half': 4,
                    'stereo_top_and_bottom': 8, 'stereo_frame_packing': 16, 'stereo_side_by_side_full': 32,
                    'stereo_anaglyph_modern': 64, 'stereo_anaglyph_crt': 128,
                    'stereo_rows_left_first': 256, 'stereo_rows_right_first': 512,
                    'stereo_columns_left_first': 1024, 'stereo_columns_right_first': 2048,
                    'stereo_checkerboard_left_first': 4096, 'stereo_checkerboard_right_first': 8192,
                    'virtual_stereo': 16384,
                    'stereo_sequential_left_first': 262144,
                    'stereo_sequential_right_first': 524288}
        self.assertEqual(values, expected)
        pair_event = protocol.find("interface[@name='kde_output_device_v2']/event[@name='stereo_pair']")
        self.assertEqual(pair_event.get('since'), '24')
        self.assertEqual([(a.get('name'), a.get('type')) for a in pair_event.findall('arg')],
                         [('partner', 'string'), ('mode', 'uint'), ('role', 'uint'), ('reflection', 'uint')])

    def test_management(self):
        protocol = ET.parse(ROOT / 'kde-output-management-v2.xml')
        for name in ('kde_output_management_v2', 'kde_output_configuration_v2'):
            self.assertEqual(protocol.find(f"interface[@name='{name}']").get('version'), '24')
        request = protocol.find("interface[@name='kde_output_configuration_v2']/request[@name='set_stereo_formats']")
        self.assertEqual(request.get('since'), '24')
        self.assertEqual([(a.get('name'), a.get('type')) for a in request.findall('arg')],
                         [('outputdevice', 'object'), ('anaglyph', 'uint'), ('other_stereo_formats', 'uint')])
        self.assertEqual(request.find('arg').get('interface'), 'kde_output_device_v2')
        pair = protocol.find("interface[@name='kde_output_configuration_v2']/request[@name='set_stereo_pair']")
        self.assertEqual(pair.get('since'), '24')
        self.assertEqual([(a.get('name'), a.get('type')) for a in pair.findall('arg')],
                         [('outputdevice', 'object'), ('partner', 'object'), ('mode', 'uint'), ('role', 'uint'), ('reflection', 'uint')])
        self.assertEqual(pair.find("arg[@name='partner']").get('allow-null'), 'true')


if __name__ == '__main__':
    unittest.main()
