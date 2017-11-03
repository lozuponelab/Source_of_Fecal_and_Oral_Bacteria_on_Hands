import argparse
import pandas as pd
from glob import glob
from os import path

def main(args):
    # read in all sink predictions and make mega dataframe
    sink_predictions = []
    folders = glob(path.join(args.input_dir, '*'))
    for folder in folders:
        try:
            if args.std_dev:
                sink_pred = pd.read_table(folder+'/sink_predictions_stdev.txt', index_col=0)
            else:
                sink_pred = pd.read_table(folder+'/sink_predictions.txt', index_col=0)
        except IOError:
            print folder
            continue
        sink_predictions.append(sink_pred)

    sink_predictions = pd.concat(sink_predictions)
    sink_predictions = sink_predictions.sort_index()
    
    with open(args.output_fp, 'w') as f:
        f.write(sink_predictions.to_csv(sep='\t'))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-i", "--input_dir", help="Directory of results files from running sourcetracker", required=True)
    parser.add_argument("-o", "--output_fp", help="Data table file path", default="results.txt")
    parser.add_argument("--std_dev", help="Merge standard deviations and not just predictions", default=False, action="store_true")
    args = parser.parse_args()
    main(args)
