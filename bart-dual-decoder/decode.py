import torch
import subprocess
import argparse
from tqdm import tqdm
from fairseq.models.bart import BARTModel


def count_file_lines(file_path):
    """
    Counts the number of lines in a file using wc utility.
    :param file_path: path to file
    :return: int, no of lines
    """
    num = subprocess.check_output(['wc', '-l', file_path])
    num = num.decode('utf-8').split(' ')
    return int(num[0])


def decode(args):
    bart = BARTModel.from_pretrained(
        args.checkpoint_dir,
        checkpoint_file=args.checkpoint_file,
        data_name_or_path=args.data_name_or_path,
        decoder_number=args.decoder_number
    )

    bart.cuda()
    bart.eval()
    bart.half()
    count = 1

    line_count = count_file_lines('{}/test.source'.format(args.data_dir))
    with open('{}/test.source'.format(args.data_dir)) as source, \
            open(args.output_file, 'w') as fout:
        sline = source.readline().strip()
        slines = [sline]
        for sline in tqdm(source, total=line_count):
            if count % args.batch_size == 0:
                with torch.no_grad():
                    hypotheses_batch = bart.sample(slines,
                                                   beam=args.beam_size,
                                                   lenpen=args.lenpen,
                                                   max_len_b=args.max_len_b,
                                                   min_len=args.min_len,
                                                   no_repeat_ngram_size=args.no_repeat_ngram_size)

                for hypothesis in hypotheses_batch:
                    fout.write(hypothesis + '\n')
                    fout.flush()
                slines = []

            slines.append(sline.strip())
            count += 1

        if slines != []:
            hypotheses_batch = bart.sample(slines,
                                           beam=args.beam_size,
                                           lenpen=args.lenpen,
                                           max_len_b=args.max_len_b,
                                           min_len=args.min_len,
                                           no_repeat_ngram_size=args.no_repeat_ngram_size)
            for hypothesis in hypotheses_batch:
                fout.write(hypothesis + '\n')
                fout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints/',
                        help="Path of checkpoint directory")
    parser.add_argument('--checkpoint_file', type=str, default='checkpoint_best.pt',
                        help="Path of checkpoint directory")
    parser.add_argument('--data_dir', type=str, required=True, help="Path of data directory")
    parser.add_argument('--data_name_or_path', type=str, required=True, help="Path of the binary data directory")
    parser.add_argument('--output_file', type=str, required=True, help="Path of the output file")
    parser.add_argument('--beam_size', type=int, default=1)
    parser.add_argument('--max_len_b', type=int, default=60)
    parser.add_argument('--min_len', type=int, default=1)
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--no_repeat_ngram_size', type=int, default=3)
    parser.add_argument('--lenpen', type=float, default=1.0)
    
    # dual decoder only arguments
    # here we use the original BART to do the inference decoder-by-decoder
    parser.add_argument('--decoder_number', type=int, choices=[1, 2], required=True)
    
    args = parser.parse_args()
    decode(args)
