from pathlib import Path
from glob import glob


def find_median_one_ups(df_table):
    median_one_up = np.floor(df_table.shape[0]/2) + 1
    result_df = pd.DataFrame(columns=['pattern', 'peak'])
    print(median_one_up)

    for column in df_table:
        idx = df_table[column].rank(method='first') == median_one_up
        true_rows = df_table[column].index[idx]
        result_df.loc[column] = true_rows.values[0], df_table.loc[true_rows,
                                                                column].values[0]
    return result_df



def make_par(catg_file_path, stm_file_path, parameters):
    return f"""# BEGIN
Cat file :{Path(catg_file_path).stem}.catg
Stm file :{Path(stm_file_path).stem}.stm
Lumped kc:T
Verbosity:3
Lossmodel:1
Num ISA  :1
ISA 1    :{parameters.kc},{parameters.m}
Num burst:1
ISA 1    :{parameters.il},{parameters.cl}
# END"""    
    
def make_par_files(file_list, output_dir, k=10, m=0.8, il=20, cl=2):
    files = [file for file_pattern in file_list for file in glob(str(file_pattern))]
    cfiles = [file for file in files if file.endswith('.catg')]
    sfiles = [file for file in files if file.endswith('.stm')]
    output_files = {}

    for cfile in cfiles:
        for sfile in sfiles:
            fn = Path(output_dir) / f'{Path(cfile).stem}_{Path(sfile).stem}.par'
            output_files[fn] = f"""# BEGIN
Cat file :{Path(cfile).stem}.catg
Stm file :{Path(sfile).stem}.stm
Lumped kc:T
Verbosity:3
Lossmodel:1
Num ISA  :1
ISA 1    :{k},{m}
Num burst:1
ISA 1    :{il},{cl}
# END"""

    return output_files
