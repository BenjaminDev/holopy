import holopy
import os
import numpy
import yaml
from scatterpy.theory.scatteringtheory import ElectricField

from numpy.testing import (assert_array_almost_equal, assert_almost_equal,
                           assert_allclose)
import numpy.testing


wavelen = 658e-9
ypolarization = [0., 1.0] # y-polarized
xpolarization = [1.0, 0.] # x-polarized
divergence = 0
pixel_scale = [.1151e-6, .1151e-6]
index = 1.33

yoptics = holopy.optics.Optics(wavelen=wavelen, index=index,
                               pixel_scale=pixel_scale,
                               polarization=ypolarization,
                               divergence=divergence)
    
xoptics = holopy.optics.Optics(wavelen=wavelen, index=index,
                               pixel_scale=pixel_scale,
                               polarization=xpolarization,
                               divergence=divergence)

optics=yoptics

def assert_allclose(actual, desired, err_msg='', verbose=True):
    if isinstance(actual, ElectricField):
        actual = actual._array()
    if isinstance(desired, ElectricField):
        desired = desired._array()
        
    numpy.testing.assert_allclose(actual, desired, err_msg=err_msg,
                        verbose=verbose)

def verify(result, name):
    gold_name = os.path.join('gold', 'gold_'+name)
    if os.path.exists(gold_name + '.npy'):
        gold = numpy.load(gold_name + '.npy')
        assert_allclose(result, gold)

    gold = yaml.load(file(gold_name+'.yaml'))

    for key, val in gold.iteritems():
        if isinstance(result, ElectricField):
            comp, check = key.split('.')
            assert_almost_equal(getattr(getattr(result, comp), check)(), val)
        else:
            assert_almost_equal(getattr(result, key)(), val)
    

def make_golds(result, name):
    '''
    Make new golds for a test

    Parameters
    ----------
    result: Hologram or ElectricField
        A result that you want to make the new gold (try to make sure it is
        correct)
    name: string
        The name for the result (this should be something like the test name)
    '''
    
    gold_name = 'gold_'+name
    if isinstance(result, ElectricField):
        numpy.save(gold_name+'.npy', result._array())
    else:
        numpy.save(gold_name+'.npy', result)

    gold_dict = {}

    checks = ['min', 'max', 'mean', 'std']


    for check in checks:
        if isinstance(result, ElectricField):
            comps = ['x_comp', 'y_comp', 'z_comp']
            for comp in comps:
                res = getattr(getattr(result, comp), check)()
                gold_dict['{0}.{1}'.format(comp, check)] = res
        else:
            gold_dict[check] = getattr(result, check)()

    yaml.dump(gold_dict, file(gold_name+'.yaml','w'))
        