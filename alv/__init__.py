from Bio import AlignIO
from colorama import init as colorama_init, Fore, Back, Style
import argparse
import sys

from .get_terminal_size import get_terminal_size

def colorizer(c):
    if c in 'AILMFWVC':
        return Back.BLUE + c
    elif c in 'KR':
        return Back.RED + c
    elif c in 'ED':
        return Back.MAGENTA + c
    elif c in 'NQST':
        return Back.GREEN + c
    elif c in 'G':
        return Back.YELLOW + c
    elif c in 'P':
        return Back.YELLOW + c
    elif c in 'HY':
        return Back.CYAN + c
    elif c in "*!":
        return Back.BLACK + Fore.WHITE + Style.BRIGHT + c + Fore.BLACK + Style.NORMAL
    else:
        return Back.WHITE + c

def colorize_sequence_string(s):
    colored_s = ''
    for c in s:
        colored_s += colorizer(c)
    return colored_s + Style.RESET_ALL

def get_accession_widths(alignment):
    '''
    Compute the space needed for all accessions, plus one for
    a delimiter.
    '''
    max_accession_length = 5        # initial guess, or minimum
    for record in alignment:
        if len(record.id) + 1 > max_accession_length:
            max_accession_length = len(record.id) + 1
    return max_accession_length

def print_one_sequence_block(rec, left_margin, start, block_width):
    colored_string = colorize_sequence_string(rec.seq[start : start + block_width])
    print("{0:{width}}{1}".format(rec.id, colored_string, width=left_margin))

def get_block_width(al_width, left_margin):
    '''
    We want to break a long alignent up into blocks. If so, how big blocks?
    Take the margin size (for accessions) into account and avoid ending up
    with blocks of size 1.
    '''
    terminal_width = get_terminal_size()[0]
    last_block_width = al_width % (terminal_width - left_margin)
    n_blocks = al_width // (terminal_width - left_margin) # Not counting last block, if uneven

    if last_block_width == al_width:
        # Short alignment, fits in one block
        return al_width
    elif last_block_width > 10:
        return terminal_width - left_margin
    else:
        sacrifice = max([1, (10 - last_block_width) // n_blocks])
        print('sacrifice:', sacrifice)
        return terminal_width - left_margin - sacrifice

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('infile')
    ap.add_argument('-c', '--color-scheme', choices=['clustal', 'zappo', 'taylor', 'hydrophobicity'], default='clustal', help='Color scheme for AA and coding DNA. The clustal coloring scheme is an approximation of the original, due to the limited color choices for consoles.')
    ap.add_argument('-f', '--format', choices=['fasta', 'clustal', 'phylip', 'stockholm', 'macse'], default='aa', help="Specify what sequence type to assume. With the 'macse' option (which refers to MACSE alignment software), coding DNA sequences in FASTA format are assumed, and frameshifts are assumed to be indicated with exclamation points. For the other formats, you may want to suggest a sequence type (see the '-t' option).")
    ap.add_argument('-k', '--keep-colors-when-redirecting', action='store_true', help='Do not strip colors when redirecting to stdout, or similar.')
    ap.add_argument('-t', '--type', choices=['aa', 'dna', 'codon', 'guess'], default='guess', help="Specify what sequence type to assume. Coding DNA is assumed with the 'codon' option. Guessing the format only chooses between 'aa' and 'dna'.")
    ap.add_argument('-w', '--width', type=int, default=0, help='Width of alignment blocks. Defaults to terminal width minus accession width, essentially.')
#    ap.add_argument('-p', '--prefix', type=int, default=0, help='Number of characters to remove from the beggining of the accession. Note: PHYLIP format allows max 10 character accessions.')
    args = ap.parse_args()

    alignment = AlignIO.read(args.infile, "fasta")
    al_width = alignment.get_alignment_length()
    left_margin = get_accession_widths(alignment)
    if args.width == 0:
        block_width = get_block_width(al_width, left_margin)
    else:
        block_width = args.width

    # Set up colors
    if args.keep_colors_when_redirecting:
        colorama_init(strip=False)
    else:
        colorama_init()

    for start in range(0, al_width, block_width):
        for record in alignment:
            print_one_sequence_block(record, left_margin, start, block_width)
        print(' ' * left_margin, start, sep='')

if __name__ == '__main__':
    main()
    