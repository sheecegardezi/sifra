__author__ = 'sudipta'

import unittest
import cPickle
import os
import numpy as np

from sira.sira import calc_loss_arrays
from sira.siraclasses import ScenarioDataGetter, Facility, Scenario
from sira.sira import power_calc


class TestSira(unittest.TestCase):
    def test_calc_loss_arrays(self):
        SETUPFILE = 'tests/config_ps_X_test.conf'
        SETUPFILE = os.path.join(os.getcwd(), SETUPFILE)
        print ('using default test setupfile')
        scenario = Scenario(SETUPFILE)
        facility = Facility('tests/config_ps_X_test.conf')
        """
        :return: tests the calc_loss_arrays function, which is the main.
        """
        print '======================Testing serial run ============================='
        component_resp_df = power_calc(facility, scenario)
        ids_comp_vs_haz, sys_output_dict, component_resp_dict = calc_loss_arrays(facility, scenario,
                                                    component_resp_df, parallel_or_serial=0)
        test_ids_comp_vs_haz = cPickle.load(open('tests/ids_comp_vs_haz.pick', 'rb'))
        test_sys_output_dict = cPickle.load(open('tests/sys_output_dict.pick', 'rb'))
        for k, v in ids_comp_vs_haz.iteritems():
            self.assertEqual(v.shape, (scenario.num_samples, facility.num_elements), msg='size mismatch')

        for k in ids_comp_vs_haz:
            np.testing.assert_array_equal(ids_comp_vs_haz[k], test_ids_comp_vs_haz[k], 'arrays not equal', verbose=True)
        #
        for k in sys_output_dict:
            np.testing.assert_array_equal(sys_output_dict[k], test_sys_output_dict[k], 'arrays not equal', verbose=True)

    def test_calc_loss_arrays_parallel(self):
        SETUPFILE = 'tests/config_ps_X_test.conf'
        SETUPFILE = os.path.join(os.getcwd(), SETUPFILE)
        print ('using default test setupfile')
        scenario = Scenario(SETUPFILE)
        facility = Facility('tests/config_ps_X_test.conf')
        """
        :return: tests the calc_loss_arrays function, which is the main.
        """
        print '======================Testing parallel run ============================='
        component_resp_df = power_calc(facility, scenario)
        ids_comp_vs_haz, sys_output_dict, component_resp_dict = calc_loss_arrays(facility, scenario,
                                                    component_resp_df, parallel_or_serial=1)
        test_ids_comp_vs_haz = cPickle.load(open('tests/ids_comp_vs_haz.pick', 'rb'))
        test_sys_output_dict = cPickle.load(open('tests/sys_output_dict.pick', 'rb'))
        for k, v in ids_comp_vs_haz.iteritems():
            self.assertEqual(v.shape, (scenario.num_samples, facility.num_elements), msg='size mismatch')

        for k in ids_comp_vs_haz:
            np.testing.assert_array_equal(ids_comp_vs_haz[k], test_ids_comp_vs_haz[k], 'arrays not equal', verbose=True)
        #
        for k in sys_output_dict:
            np.testing.assert_array_equal(sys_output_dict[k], test_sys_output_dict[k], 'arrays not equal', verbose=True)


    def test_extreme_values(self):

        # sys_output_dict # should be full when 0, and 0 when hazard level 10

        scenario = Scenario('tests/config_ps_X_test_extremes.conf')
        facility = Facility('tests/config_ps_X_test_extremes.conf')
        component_resp_df = power_calc(facility, scenario)

        ids_comp_vs_haz, sys_output_dict, component_resp_dict = calc_loss_arrays(facility, scenario,
                                                    component_resp_df, parallel_or_serial=1)

        for k, v in component_resp_dict.iteritems():
            for kk, vv in v.iteritems():
                if k == scenario.PGA_str[0] and kk[1] == 'func_mean':
                    self.assertEqual(vv, 1.0)
                if k == scenario.PGA_str[0] and kk[1] == 'loss_mean':
                    self.assertEqual(vv, 0.0)
                # if k == scenario.PGA_str[1] and kk[1] == 'func_mean':
                #     print k, kk, vv, '<<<-----------------------'
                #     self.assertEqual(vv, 0.0, 'test for {} failed for PGA Level: {}'.format(kk[0], k))
                # if k == scenario.PGA_str[1] and kk[1] == 'loss_mean':
                #     print k, kk, vv, '<<<-----------------------'
                #     self.assertAlmostEqual(vv, 1.0)



if __name__ == '__main__':
    unittest.main()
