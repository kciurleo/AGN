#this file implements the functions which define the expected Cstat and its
#variance as defined in Kaastra 2017
#Can be used to produce a goodness of fit type statistic in cstat


#ideally would this or another program should be able to be passed
#a model and a spectrum and calculate Chi^2 analog
import numpy as np
import math as m


#returns the value of the possion likelihood distribution for values of mu and k
#k must be an integer
def P(mu,k):
    return m.e**(-mu) * mu**k / m.factorial(k)

#returns the value of C_e,i
#The expected contribution to the total c stat from a particular bin given a
#value of expected counts mu
def Cei(mu,eps):
    sum = 0
    last_term = 0
    this_term = P(mu,0) * mu
    sum += this_term
    k = 1

    while abs(this_term - last_term) > eps:
        last_term = this_term
        this_term = P(mu,k) * (mu - k + k*m.log(k/mu))
        sum += this_term
        k += 1

    return 2*sum

#Svi needed in the calculation of the variance
def Svi(mu,eps):
    sum = 0
    last_term = 0
    this_term = P(mu,0) * mu**2

    sum += this_term
    k = 1
    while abs(this_term - last_term) > eps:
        last_term = this_term
        this_term = P(mu,k) * (mu - k + k*m.log(k/mu))**2
        sum += this_term
        k += 1

    return 4*sum

#returns the value of C_v,i
#The variance of C_e,i
def Cvi(mu,eps):
    return Svi(mu,eps) - Cei(mu,eps)**2


#returns the value of
if __name__ == '__main__':
    print(Cvi(1,.00001))
