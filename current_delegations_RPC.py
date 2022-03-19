# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 21:32:25 2022

@author: piyus
"""
import requests
import pandas as pd
import json

"""
Get delegations of a given address
"""
def get_address_delegations(address):
    
    url_for_delegations = "https://api.cosmos.network/cosmos/staking/v1beta1/delegations/"+address+"?pagination.offset=0"
    response = requests.get(url_for_delegations)
    delegations = pd.DataFrame(json.loads(response.content)['delegation_responses'])
    address_delegation = pd.DataFrame(delegations['delegation'].to_list())
    
    return address_delegation


"""
Get delegations belonging to the Interchain foundation's multisig addresses
"""     
def get_icf_delegations(icf_multi_sigs):
    
    delegations_data = pd.DataFrame(columns = ['delegator_address', 'validator_address','shares'])
    
    for address in icf_multi_sigs:
        address_delegation = get_address_delegations(address)
        delegations_data = pd.concat([delegations_data, address_delegation], axis = 0)
        
    return delegations_data


"""
Get the latest 150 validator set data
"""
def get_validator_set():
    
    url_for_validators = "https://api.cosmos.network/cosmos/staking/v1beta1/validators?pagination.offset=150"
    response = json.loads(requests.get(url_for_validators).content)['validators']    
    validators = pd.DataFrame(response)    
    validators_description  = pd.DataFrame(validators['description'].to_list())
    validators = validators.join(validators_description, how = "left")    
    validators = validators[['operator_address',
                            'moniker',
                            'website',
                            'details',
                            'tokens',
                            'jailed']]    
    return validators


"""
Merge the validator data and delegations data to produce a detailed validator data set for delegations
"""
def merge_delegation_validator_data(delegations_data, validators):
    delegations_data.set_index('validator_address')
    validators.set_index('operator_address')
    
    merged_data = delegations_data.join(validators, how = 'left')
    return merged_data


"""
Multisig data obtained from 
https://github.com/cosmos/mainnet/blob/master/accounts/icf/multisig.json
"""
icf_multi_sigs = ["cosmos1unc788q8md2jymsns24eyhua58palg5kc7cstv",
                  "cosmos1z8mzakma7vnaajysmtkwt4wgjqr2m84tzvyfkz"] 

icf_delegations_data = get_icf_delegations(icf_multi_sigs)

validators = get_validator_set()

detailed_delegations = merge_delegation_validator_data(icf_delegations_data, validators)

detailed_delegations.to_csv('icf_delegations.csv')
    
        
    
    


        
    