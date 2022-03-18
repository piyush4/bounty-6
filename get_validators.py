# -*- coding: utf-8 -*-
"""
Created on Fri Mar 18 12:27:23 2022

@author: piyus
"""

import urllib.request, json
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json

"""
Function returns top 100 delegators of all validators (Assumption is ICF delegations
would be large enough and be included in the top 100 delegator of each validator).

Mintscan API does not allow simple queries from Python, so had to include a user agent.
There is a limit of 50 delegators per query.

"""
def get_top_delegators(validator_address, moniker):
    
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
    delegators_data = pd.DataFrame(columns = ['delegator_address', 'amount'])
    offset = [0,50]
    for i in offset:
        url_for_delegators = "https://api.mintscan.io/v1/cosmos/validators/"+validator_address+"/delegators?limit=50&offset="+str(i)
        response = requests.get(url_for_delegators, headers=headers)
        
        all_delegators = json.loads(response.content)['delegators']
        all_delegators = pd.DataFrame(all_delegators)
        delegators_data = pd.concat([delegators_data,all_delegators], axis = 0)
    
    delegators_data.insert(0, 'moniker', moniker)
    
    return delegators_data

"""get validator list"""

url = "https://api.cosmostation.io/v1/staking/validators"
response  = urllib.request.urlopen(url)
all_validators = json.loads(response.read())
validator_data = pd.DataFrame(all_validators)
validator_data = validator_data[['account_address',
                                'operator_address',
                                'moniker']]

"""
ICF multi_sigs_list obtained from: 
https://github.com/cosmos/mainnet/blob/master/accounts/icf/multisig.json
Verified the account balances.
"""
    
icf_multi_sigs = ["cosmos1unc788q8md2jymsns24eyhua58palg5kc7cstv",
                  "cosmos1z8mzakma7vnaajysmtkwt4wgjqr2m84tzvyfkz"] 


"""
Get a list of top 100 delegators of all validators.
This part will take a while to run since it calls the API for each validator.
Around 355*2 API calls.
"""

all_delegators_data = pd.DataFrame(columns = ['delegator_address', 'amount', 'moniker'])

for _,_,operator_address, moniker in validator_data.itertuples():
    print(operator_address, moniker)
    top_100_delegators = get_top_delegators(operator_address,  moniker)
    if len(top_100_delegators.index)>50:
        all_delegators_data = pd.concat([all_delegators_data,top_100_delegators], axis = 0)

"""Filter out ICF delegations and their amounts and sort them"""

icf_delegations = all_delegators_data[all_delegators_data['delegator_address'].isin(icf_multi_sigs)]
icf_delegations = icf_delegations.sort_values(['delegator_address', 'amount'], ascending=False)

  

   





