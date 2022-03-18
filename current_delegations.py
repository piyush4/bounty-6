# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 18:56:58 2022

@author: piyus
"""
import requests
import pandas as pd
import json
import urllib.request

"""
Process the data into the dataframe for each multi-sig address
"""
def get_delegations_for_address(delegations):
    delegations_for_address = pd.DataFrame(columns = ["delegator_address", "validator_address", "shares"])
    k = 0
    for delegation in delegations:
        delegations_for_address = pd.concat([delegations_for_address, 
                                             pd.DataFrame(delegation["delegation"], index= [k])],
                                             axis = 0)
        k = k+1
    return delegations_for_address

"""
Query the API for delegations of a particular address
"""

def get_delegation_data(icf_multi_sigs):
    
    delegation_data = pd.DataFrame(columns = ["delegator_address","validator_address","shares"])
    for address in icf_multi_sigs:
        url_for_delegations = "https://lcd-cosmos.cosmostation.io/cosmos/staking/v1beta1/delegations/"+address+"?pagination.limit=1000"
        response = requests.get(url_for_delegations, headers = headers)
        delegations = json.loads(response.content)["delegation_responses"]
        delegation_for_address = get_delegations_for_address(delegations)
        delegation_data = pd.concat([delegation_data, delegation_for_address])
    delegation_data.set_index('validator_address')   
    return delegation_data


"""
Get the validator list
"""
def get_validator_list():
    validators_url = "https://api.cosmostation.io/v1/staking/validators"
    response  = urllib.request.urlopen(validators_url)
    all_validators = json.loads(response.read())
    validator_data = pd.DataFrame(all_validators)
    validator_data = validator_data[['account_address',
                                    'operator_address',
                                    'moniker',
                                    'website',
                                    'details']]
    
    validator_data.rename(columns = {'account_address':'validator_account_address',
                                     'operator_address':'validator_address'}, inplace=True)
    return validator_data


"""
ICF multi_sigs_list obtained from: 
https://github.com/cosmos/mainnet/blob/master/accounts/icf/multisig.json
Verified the account balances.
"""
    
icf_multi_sigs = ["cosmos1unc788q8md2jymsns24eyhua58palg5kc7cstv",
                  "cosmos1z8mzakma7vnaajysmtkwt4wgjqr2m84tzvyfkz"] 

"""
User Agent required in headers because mintscan does not allow direct Python queries.
"""

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

delegation_data = get_delegation_data(icf_multi_sigs)

validator_data = get_validator_list()

delegation_data = delegation_data.join(validator_data.set_index('validator_address'),
                                       on = 'validator_address', how="left")


delegation_data.to_csv('ICF_delegations.csv',index=False)

    
    





