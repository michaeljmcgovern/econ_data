#%%
import requests
import pandas as pd

#%%
PRINT = True
URL = 'https://sdmx.ilo.org/rest/data/ILO,DF_'
OUT_DIR = 'ILO/Raw/'

#%%
def get_ilo(dataset:    str, 
            country:    str,
            params:     dict[str:list[str]], 
            print_data: bool=False
            ) -> pd.DataFrame:
    if country:
        url = f'{URL}{dataset}/{country}.....'
    else:
        url = f'{URL}{dataset}'

    # Pull request
    print(f'\nPulling data from ILO: {dataset}')
    r = requests.get(url, params)
    response = r.status_code
    if response != 200:
        raise KeyError(f"HTML error: {response}")


    #%%
    # Process data
    print('Processing data')
    
    json = r.json()['data']

    # Metadata
    meta = json['structures'][0]
    ## Get name
    name = meta['name']

    ## Get dimensions
    dims = meta['dimensions']['series']
    times = meta['dimensions']['observation'][0]
    attrs = meta['attributes']['observation']
    units = meta['attributes']['series']
    
    dims_id = {dim['id']: [v['id'] for v in dim['values']] for dim in dims}
    dims_id[times['id']] = [t['id'] for t in times['values']]
    
    dims_name = {dim['name']: [v['name'] for v in dim['values']] for dim in dims}
    dims_name[times['name']] = [t['name'] for t in times['values']]

    attrs_id = {attr['id']: [list(v.values())[0] for v in attr['values']] for attr in attrs}    
    units_id = {unit['id']: unit['values'][0]['name'] for unit in units}


    # Data
    data = json['dataSets'][0]['series']
    data = {f'{k}:{t}': v['observations'][t] for k, v in data.items() for t in v['observations']}
    data = pd.DataFrame(data).T
    

    # Process labels
    ## Index labels - ID
    data = data.reset_index()
    data[list(dims_id.keys())] = data['index'].str.split(':', expand=True)
    for dim, labels in dims_id.items():
        labels = {str(n): label for n, label in enumerate(labels)}
        data[dim] = data[dim].replace(labels)
    
    ## Index labels - ID
    data[list(dims_name.keys())] = data['index'].str.split(':', expand=True)
    for dim, labels in dims_name.items():
        labels = {str(n): label for n, label in enumerate(labels)}
        data[dim] = data[dim].replace(labels)



    ## Values (first column)
    data = data.rename(columns={0: 'Value'})
    
    ## Notes (other columns)
    data = data.rename(columns={n: attr for n, attr in enumerate(attrs_id, start=1)})
    for col, attr in attrs_id.items():
        attr = {n: a for n, a in enumerate(attr)}
        if len(attr):
            data[col] = data[col].replace(attr)
    
    data['DS'] = dataset
    data['Dataset'] = name
    for col, unit in units_id.items():
        data[col] = unit

    # Reorder columns
    dims = [col for id_, name in zip(dims_id, dims_name) for col in [id_, name]]
    units = list(units_id.keys())
    notes = list(attrs_id.keys())
    cols = ['DS', 'Dataset'] + dims + units + ['Value'] + notes
    data = data[cols]


    #%%
    # Print to CSV
    if print_data:
        print('Printing to CSV')
        data.to_csv(f'{OUT_DIR}/{dataset}.csv', index=None)

    return dims


#%%
if __name__ == '__main__':
    dataset = 'EMP_TEMP_SEX_STE_OCU_NB'
    country = None
    params = {
              'format':        'jsondata',
              'startPeriod':   '2014-01-01',
              'endPeriod':     '2014-12-31',
             }

# %%
    data = get_ilo(dataset, country, params, print_data=PRINT)


