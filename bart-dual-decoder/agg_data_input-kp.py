import sys

sys.path.insert(0, '..')

import os
import json
from tqdm import tqdm
from pathlib import Path
from deepkp.inputters import constants

DATA_DIR = '../data/'


def process(infile, outdir, split):
    Path(outdir).mkdir(parents=True, exist_ok=True)
    with open(infile, "r", encoding='utf-8') as fin, \
            open(os.path.join(outdir, '{}.source'.format(split)), 'w', encoding='utf-8') as fsrc, \
            open(os.path.join(outdir, '{}.target1'.format(split)), 'w', encoding='utf-8') as ftgt1, \
            open(os.path.join(outdir, '{}.target2'.format(split)), 'w', encoding='utf-8') as ftgt2:
        for line in tqdm(fin):
            ex = json.loads(line)
            source = ex['title']['text'] + ' {} '.format(constants.TITLE_SEP) + ex['abstract']['text']
            kps = ex['present_kps']['text'] + ex['absent_kps']['text']
            target = ' {} '.format(constants.KP_SEP).join([t for t in kps if t])
            if len(source) > 0 and len(target) > 0:
                fsrc.write(source + '\n')
                ftgt1.write(target + '\n')
                ftgt2.write(target + '\n')


if __name__ == '__main__':
    #process(os.path.join(DATA_DIR, 'scikp/processed/kp20k/train.json'), 'data/kp20k', 'train')
    #process(os.path.join(DATA_DIR, 'scikp/processed/kp20k/valid.json'), 'data/kp20k', 'valid')
    #process(os.path.join(DATA_DIR, 'scikp/processed/kp20k/test.json'), 'data/kp20k', 'test')
    process(os.path.join(DATA_DIR, 'kptimes-dual-debug/processed/train.json'), 'data/kptimes-dual-debug', 'train')
    process(os.path.join(DATA_DIR, 'kptimes-dual-debug/processed/valid.json'), 'data/kptimes-dual-debug', 'valid')
    process(os.path.join(DATA_DIR, 'kptimes-dual-debug/processed/test.json'), 'data/kptimes-dual-debug', 'test')
    #process(os.path.join(DATA_DIR, 'kptimes-eda5/processed/train.json'), 'data/kptimes-eda5', 'train')
    #process(os.path.join(DATA_DIR, 'kptimes-eda5/processed/valid.json'), 'data/kptimes-eda5', 'valid')
    #process(os.path.join(DATA_DIR, 'kptimes-eda5/processed/test.json'), 'data/kptimes-eda5', 'test') 
