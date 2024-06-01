#%%
import requests
import pandas as pd


PRINT = True
URL = 'https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/'
OUT_DIR = 'Raw/'


def get_eurostat(dataset:    str, 
                 params:     dict[str:list[str]], 
                 print_data: bool=True
                 ) -> pd.DataFrame:
    
    # Pull request
    print(f'\nPulling data from Eurostat: {dataset}')
    r = requests.get(URL+dataset, params)
    response = r.status_code
    if response != 200:
        raise KeyError(f"HTML error: {response}")
    data = r.json()


    # Process data
    print('Processing data')
    
    ## Get labels
    labels = data['dimension']
    labels = {dim: list(labels[dim]['category']['label'].values()) for dim in labels}
    labels = pd.MultiIndex.from_product(labels.values(), names=labels.keys())
    labels = pd.DataFrame(range(len(labels)), index=labels, columns=['n']).reset_index()
    
    ## Get data
    df = pd.Series(data['value'])
    df.index = df.index.astype(int)
    df = df.sort_index()
    df = df.reset_index()
    df.columns = 'n', 'Value'

    ## Merge labels & data
    df = labels.merge(df, on='n', how='right')
    df = df.drop(columns='n')


    # Print to CSV
    if print_data:
        print('Printing to CSV')
        df.to_csv(f'{OUT_DIR}/{dataset}.csv', index=None)


    return df


#%%
if __name__ == '__main__':
    dataset = 'nama_10_gdp'

    params = {
              'format':     'JSON',
              # 'geo':        'EU27_2020',
              # 'time':       ['2018', '2019'],
              # 'freq':       'a',
              # 'unit':       'clv15_meur',
              # 'na_item':    ['b1gq', 'b1g'] 
             }

    data = get_eurostat(dataset, params, print_data=PRINT)
