#!/usr/bin/env bash

SRCDIR=data

# if [[ ! -d bart.base ]]; then
#     wget -N https://dl.fbaipublicfiles.com/fairseq/models/bart.base.tar.gz
#     tar -xvzf bart.base.tar.gz
#     rm bart.base.tar.gz
# fi
# if [[ ! -d bart.large ]]; then
#     wget -N https://dl.fbaipublicfiles.com/fairseq/models/bart.large.tar.gz
#     tar -xvzf bart.large.tar.gz
#     rm bart.large.tar.gz
# fi
# for filename in "encoder.json" "vocab.bpe" "dict.txt"; do
#     if [[ ! -f $filename ]]; then
#         wget -N https://dl.fbaipublicfiles.com/fairseq/gpt2_bpe/${filename}
#     fi
# done

# if [[ ! -d $SRCDIR ]]; then
#     python agg_data.py
# fi

DICT_FILE=bart.base/dict.txt # dict.txt

function bpe_preprocess () {

for SPLIT in train valid test; do
  for LANG in source target1 target2; do
    python encode.py \
        --encoder-json encoder.json \
        --vocab-bpe vocab.bpe \
        --inputs "$SRCDIR/$TASK/$SPLIT.$LANG" \
        --outputs "$SRCDIR/$TASK/$SPLIT.bpe.$LANG" \
        --max_len 510 \
        --workers 60;
  done
done

}

function process () {

fairseq-preprocess \
--source-lang "source" \
--target-lang "target1" \
--trainpref "$SRCDIR/${TASK}/train.bpe" \
--validpref "$SRCDIR/${TASK}/valid.bpe" \
--testpref "$SRCDIR/${TASK}/test.bpe" \
--destdir "$SRCDIR/${TASK}-bin/" \
--workers 60 \
--srcdict $DICT_FILE \
--tgtdict $DICT_FILE;

fairseq-preprocess \
--source-lang "source" \
--target-lang "target2" \
--trainpref "$SRCDIR/${TASK}/train.bpe" \
--validpref "$SRCDIR/${TASK}/valid.bpe" \
--testpref "$SRCDIR/${TASK}/test.bpe" \
--destdir "$SRCDIR/${TASK}-bin/" \
--workers 60 \
--srcdict $DICT_FILE \
--tgtdict $DICT_FILE;

# move things around...
for subset in target1 target2; do
    for split in train valid test; do
	mv $SRCDIR/${TASK}-bin/${split}.source-${subset}.source.bin $SRCDIR/${TASK}-bin/${split}.source-target.source.bin
	mv $SRCDIR/${TASK}-bin/${split}.source-${subset}.source.idx $SRCDIR/${TASK}-bin/${split}.source-target.source.idx
	mv $SRCDIR/${TASK}-bin/${split}.source-${subset}.${subset}.bin $SRCDIR/${TASK}-bin/${split}.source-target.${subset}.bin
	mv $SRCDIR/${TASK}-bin/${split}.source-${subset}.${subset}.idx $SRCDIR/${TASK}-bin/${split}.source-target.${subset}.idx
    done
    mv $SRCDIR/${TASK}-bin/dict.${subset}.txt $SRCDIR/${TASK}-bin/dict.target.txt
done

}

function bpe_preprocess_test_only () {

for SPLIT in test; do
  for LANG in source target; do
    python encode.py \
        --encoder-json encoder.json \
        --vocab-bpe vocab.bpe \
        --inputs "$SRCDIR/$TASK/$SPLIT.$LANG" \
        --outputs "$SRCDIR/$TASK/$SPLIT.bpe.$LANG" \
        --max_len 510 \
        --workers 60;
  done
done

}

function process_test_only () {

fairseq-preprocess \
--source-lang "source" \
--target-lang "target" \
--testpref "$SRCDIR/${TASK}/test.bpe" \
--destdir "$SRCDIR/${TASK}-bin/" \
--workers 60 \
--srcdict $DICT_FILE \
--tgtdict $DICT_FILE;

}

# aggregate data first
python agg_data_input-kp.py

for task in kptimes-dual-debug; do
    TASK=$task
    bpe_preprocess
    process
done


#for task in kp20k kptimes; do 
#    TASK=$task
#    bpe_preprocess
#    process
#done
#for task in nus inspec krapivin semeval; do
#    TASK=$task
#    bpe_preprocess_test_only
#    process_test_only
#done

