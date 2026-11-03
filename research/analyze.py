"""Recompute comparison tables from the committed snapshot without an API call."""
import argparse,json
from pathlib import Path
from .study import analyze

def main():
    p=argparse.ArgumentParser();p.add_argument('input',nargs='?',type=Path,default=Path(__file__).resolve().parents[1]/'public/data/study.json');args=p.parse_args()
    data=json.loads(args.input.read_text())
    if data.get('schema_version')!=1:raise ValueError('Unsupported snapshot')
    print(json.dumps(analyze(data['pull_requests']),indent=2))
if __name__=='__main__':main()
