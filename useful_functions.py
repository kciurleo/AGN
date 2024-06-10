# Error functions
import numpy as np

def add_error_prop(errors):
    '''
    errors: an array/list of error arrays (e.g. [xerror, yerror,...])
    
    Takes in an array/list of errors and, assuming the ith value in each array is related,
    calculates the addition/subtraction uncertainty associated, using:

    sigma=sqrt(sigma_x^2+sigma_y^2+...)
    '''
    error_array=np.asarray(errors)
    return(np.sqrt(np.sum(error_array**2, axis=0)))

def mult_error_prop(values, errors):
    '''
    values: an array/list of value arrays (e.g. [xerror, yerror,...])
    errors: an array/list of error arrays (e.g. [xerror, yerror,...])
    
    Takes in an array/list of values and one of errors and, assuming the ith value in each 
    array is related, calculates the multiplication/division uncertainty associated, using:

    sigma=sqrt((sigma_x/x)^2+(sigma_y/y)^2+...)
    '''
    error_array=np.asarray(errors)
    value_array=np.asarray(values)
    return(np.sqrt(np.sum((error_array/value_array)**2, axis=0)))