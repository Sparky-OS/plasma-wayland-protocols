#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1] / 'src' / 'protocols'


class VirtualStereoContract(unittest.TestCase):
    def test_content(self):
        protocol = ET.parse(ROOT / 'kde-stereo-content-v1.xml')
        content = protocol.find(".//enum[@name='content']")
        self.assertEqual([(entry.get('name'), int(entry.get('value'))) for entry in content.findall('entry')],
                         [('none', 0), ('side_by_side_full', 3)])

    def test_device(self):
        protocol = ET.parse(ROOT / 'kde-output-device-v2.xml')
        for name in ('kde_output_device_registry_v2', 'kde_output_device_v2', 'kde_output_device_mode_v2'):
            self.assertEqual(protocol.find(f"interface[@name='{name}']").get('version'), '28')
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
                    'stereo_sequential_right_first': 524288,
                    'stereo_field_alternative': 0x100000, 'stereo_line_alternative': 0x200000,
                    'stereo_l_depth': 0x400000, 'stereo_l_depth_graphics': 0x800000}
        self.assertEqual(values, expected)
        pair_event = protocol.find("interface[@name='kde_output_device_v2']/event[@name='stereo_pair']")
        self.assertEqual(pair_event.get('since'), '24')
        self.assertEqual([(a.get('name'), a.get('type')) for a in pair_event.findall('arg')],
                         [('partner', 'string'), ('mode', 'uint'), ('role', 'uint'), ('reflection', 'uint')])

    def test_swap_eyes_and_ized3d(self):
        device = ET.parse(ROOT / 'kde-output-device-v2.xml')
        capabilities = {entry.get('name'): (int(entry.get('value'), 0), entry.get('since'))
                        for entry in device.findall("interface[@name='kde_output_device_v2']/enum[@name='capability']/entry")}
        self.assertEqual(capabilities['stereo_swap_eyes'], (0x40000, '26'))
        self.assertEqual(capabilities['ized3d_options'], (0x80000, '27'))
        swap = device.find("interface[@name='kde_output_device_v2']/event[@name='stereo_swap_eyes']")
        self.assertEqual(swap.get('since'), '26')
        self.assertEqual([(a.get('name'), a.get('type')) for a in swap.findall('arg')], [('enabled', 'uint')])
        options = device.find("interface[@name='kde_output_device_v2']/event[@name='ized3d_options']")
        self.assertEqual(options.get('since'), '27')
        self.assertEqual([(a.get('name'), a.get('type')) for a in options.findall('arg')], [('mode', 'uint'), ('transfer', 'uint')])
        management = ET.parse(ROOT / 'kde-output-management-v2.xml')
        swap = management.find("interface[@name='kde_output_configuration_v2']/request[@name='set_stereo_swap_eyes']")
        self.assertEqual(swap.get('since'), '26')
        self.assertEqual([(a.get('name'), a.get('type')) for a in swap.findall('arg')], [('outputdevice', 'object'), ('enabled', 'uint')])
        options = management.find("interface[@name='kde_output_configuration_v2']/request[@name='set_ized3d_options']")
        self.assertEqual(options.get('since'), '27')
        self.assertEqual([(a.get('name'), a.get('type')) for a in options.findall('arg')],
                         [('outputdevice', 'object'), ('mode', 'uint'), ('transfer', 'uint')])

    def test_depth_structures_and_timing(self):
        device = ET.parse(ROOT / 'kde-output-device-v2.xml')
        flags = {entry.get('name'): entry.get('since')
                 for entry in device.findall("interface[@name='kde_output_device_mode_v2']/enum[@name='flags']/entry")}
        for name in ('stereo_field_alternative', 'stereo_line_alternative', 'stereo_l_depth', 'stereo_l_depth_graphics'):
            self.assertEqual(flags[name], '28')
        capabilities = {entry.get('name'): (int(entry.get('value'), 0), entry.get('since'))
                        for entry in device.findall("interface[@name='kde_output_device_v2']/enum[@name='capability']/entry")}
        self.assertEqual(capabilities['side_by_side_full_timing'], (0x100000, '28'))
        self.assertEqual(capabilities['stereo_depth'], (0x200000, '28'))
        management = ET.parse(ROOT / 'kde-output-management-v2.xml')
        for protocol, interface in ((device, 'kde_output_device_v2'), (management, 'kde_output_configuration_v2')):
            timing = protocol.find(f"interface[@name='{interface}']/enum[@name='side_by_side_full_timing']")
            self.assertEqual([(e.get('name'), int(e.get('value'))) for e in timing.findall('entry')],
                             [('whole_line_doubled', 0), ('blanking_kept', 1)])
            source = protocol.find(f"interface[@name='{interface}']/enum[@name='stereo_depth_source']")
            self.assertEqual([(e.get('name'), int(e.get('value'))) for e in source.findall('entry')],
                             [('flat', 0), ('desktop', 1), ('desktop_and_content', 2)])
        timing = device.find("interface[@name='kde_output_device_v2']/event[@name='side_by_side_full_timing']")
        self.assertEqual(timing.get('since'), '28')
        self.assertEqual([(a.get('name'), a.get('type'), a.get('enum')) for a in timing.findall('arg')],
                         [('timing', 'uint', 'side_by_side_full_timing')])
        depth = device.find("interface[@name='kde_output_device_v2']/event[@name='stereo_depth']")
        self.assertEqual(depth.get('since'), '28')
        self.assertEqual([(a.get('name'), a.get('type')) for a in depth.findall('arg')],
                         [('source', 'uint'), ('viewing_distance', 'uint')])
        timing = management.find("interface[@name='kde_output_configuration_v2']/request[@name='set_side_by_side_full_timing']")
        self.assertEqual(timing.get('since'), '28')
        self.assertEqual([(a.get('name'), a.get('type')) for a in timing.findall('arg')],
                         [('outputdevice', 'object'), ('timing', 'uint')])
        depth = management.find("interface[@name='kde_output_configuration_v2']/request[@name='set_stereo_depth']")
        self.assertEqual(depth.get('since'), '28')
        self.assertEqual([(a.get('name'), a.get('type')) for a in depth.findall('arg')],
                         [('outputdevice', 'object'), ('source', 'uint'), ('viewing_distance', 'uint')])

    def test_native_viewport(self):
        protocol = ET.parse(ROOT / 'kde-output-device-v2.xml')
        event = protocol.find("interface[@name='kde_output_device_mode_v2']/event[@name='view_size']")
        self.assertEqual(event.get('since'), '25')
        self.assertEqual([(a.get('name'), a.get('type')) for a in event.findall('arg')],
                         [('width', 'int'), ('height', 'int')])

    def test_management(self):
        protocol = ET.parse(ROOT / 'kde-output-management-v2.xml')
        for name in ('kde_output_management_v2', 'kde_output_configuration_v2'):
            self.assertEqual(protocol.find(f"interface[@name='{name}']").get('version'), '28')
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
