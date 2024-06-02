#%%
import requests
import pandas as pd

#%%
PRINT = True
URL = 'http://api.worldbank.org/v2/country/all/indicator/'
OUT_DIR = 'World Bank/Raw/'

#%%
def get_world_bank(dataset:    str, 
                 params:     dict[str:list[str]], 
                 print_data: bool=False
                 ) -> pd.DataFrame:
    #%%
    # Pull request
    print(f'\nPulling data from Eurostat: {dataset}')
    r = requests.get(URL+dataset, params)
    response = r.status_code
    if response != 200:
        raise KeyError(f"HTML error: {response}")

    #%%
    # Process data
    print('Processing data')
    
    data = r.json()

    data = data[1]
    for c in range(len(data)):
        data[c]['country_id'] = data[c]['country']['id']
        data[c]['country_name'] = data[c]['country']['value']
        del data[c]['country']


    df = pd.DataFrame(data)

    df['indicator'] = dataset
    df['indicator_name'] = data[0]['indicator']['value']

    #%%
    # Print to CSV
    if print_data:
        print('Printing to CSV')
        df.to_csv(f'{OUT_DIR}/{dataset}.csv', index=None)


    return df


#%%
if __name__ == '__main__':
    dataset = 'NY.GDP.MKTP.KD'

    params = {
              'format':     'JSON',
              'per_page':   30000,
              # 'geo':        'EU27_2020',
            #   'date':       '2018',
              'freq':       'Y',
              # 'unit':       'clv15_meur',
              # 'na_item':    ['b1gq', 'b1g'] 
             }

# %%
    data = get_world_bank(dataset, params, print_data=PRINT)

