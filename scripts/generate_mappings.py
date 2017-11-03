import argparse
import pandas as pd
from biom import load_table
import os
from os import path
import numpy as np

def main(args):
    # read in biom table and metadata table, make output folder
    table = load_table(args.input_fp)
    meta = pd.read_table(args.mapping_fp, index_col=0)
    os.mkdir(args.output_dir)
    
    # filter biom table
    if args.min_samples is not None:
        to_keep = table.ids(axis="observation")[table.pa().sum(axis="observation") > args.min_samples]
        table.filter(to_keep, axis="observation")
    
    table.subsample(args.rarefaction_depth)
    
    # filter to humans only
    meta_keep = [i for i in meta.index if meta.loc[i, "host_common_name"]=="human"]
    meta = meta.loc[meta_keep]
    
    # sync biom table and metadata table
    in_both = set(meta.index) & set(table.ids())
    table = table.filter(in_both)
    meta = meta.loc[in_both]
    
    # write biom table to disk
    new_table_name = '.'.join(path.basename(args.input_fp).split('.')[:-1] + ['st', 'biom'])
    with open(path.join(args.output_dir, new_table_name), 'w') as f:
        f.write(table.to_tsv())
    
    # generate rows for mapping files
    sink_rows = list()
    source_rows = list()
    
    for sample in meta.index:
        if "palm" in sample.lower():
            sink_rows.append((sample, "sink", "palm"))
        else:
            source_rows.append((sample, "source", sample))
    
    # make mapping files
    columns = ("#SampleID", "SourceSink", "Env")
    source_table = pd.DataFrame(source_rows, columns=columns)
    for i, index in enumerate(xrange(0, len(sink_rows), args.per_file)):
        sink_table = pd.DataFrame(sink_rows[index: index+args.per_file], columns=columns)
        merged_table = pd.concat((source_table, sink_table), ignore_index=True)
        with open(path.join(args.output_dir, "mapping_%s.txt" % i), 'w') as f:
            f.write(merged_table.to_csv(sep='\t', index=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_fp", help="Input BIOM file", required=True)
    parser.add_argument("-m", "--mapping_fp", help="mapping file", required=True)
    parser.add_argument("-o", "--output_dir", help="Output directory", required=True)
    parser.add_argument("-s", "--min_samples", help="Minmum samples present", type=int)
    parser.add_argument("-d", "--rarefaction_depth", help="Rarefaction depth", default=1000, type=int)
    parser.add_argument("--per_file", help="Number of samples per mapping file", default=1, type=int)
    args = parser.parse_args()
    main(args)	
