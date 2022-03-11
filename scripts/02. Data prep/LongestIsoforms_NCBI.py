#! /usr/bin/env python3

import sys
import re
from itertools import groupby

print(
"""
This is LongestIsoforms_NCBI_v2.py
Usage: LongestIsoforms_NCBI_v2.py input.fa input.gff output.fa
"""
)

input_file = sys.argv[1]
input_gff = sys.argv[2]
output_file = sys.argv[3]


print("the input fasta file is: "+input_file)
print("the input gff file is: "+input_gff)


d_gene_ID = {}
#dictionary build from gff file. Gene ID as values, protein ID as keys.
search_string_gID = 'GeneID:(\d+)'
search_string_protID = ';protein_id=(\w+\.\d+)'

with open(input_gff, "r") as f:
	for line in f:
		line = line.strip()
		try:
			d_value = re.search(search_string_gID, line).group(1) #gene ID is value
			d_key = re.search(search_string_protID, line).group(1) #protein ID is key
			if d_key not in d_gene_ID.keys():
				d_gene_ID[d_key] = d_value
		except:
			pass #skips line if any re.search is "None"

def fasta_parse(fasta_file): #when given a fasta file, the function yields tuples of (header, sequence)
	with open(fasta_file) as g:
		fasta_iterator = (x[1] for x in groupby(g, lambda line: line[0] == ">")) #create alternating groups of lines starting by > and the others
		for header in fasta_iterator: 
			header_string = header.__next__()[1:].strip()		#line[0] is the ">", so everything else on the line is the header string
			sequence = "".join(s.strip() for s in fasta_iterator.__next__()) #We join all the objects in the list following the header list (groupby output)
			search_string_prot_an = '([^\s]+)\s'
			protein_AN = re.search(search_string_prot_an, header_string).group(1)
			try:
				gene_ID = d_gene_ID[protein_AN]
				yield (header_string, sequence, d_gene_ID[protein_AN]) 
			except KeyError: #happens when protein not in the gff, e.g. when gff was filtered
				pass

fasta = fasta_parse(input_file) #calls the function we defined to parse the file passed as an argument


#The groupby creates a generator, and the if and else loops iterate through it.
#If you uncomment the block with the print statements, the generator will be exhausted, so the output file (generated by the second block) will be empty.
#This can be useful if you want to have a quick look on STDOUT.
"""
output = []

for sublist_iterator in groupby(sorted(fasta, key = lambda x: x[2]), lambda x: x[2]): #group sequences by gene IDs. Groupby works only on contiguous lines, so we need to sort the lists according to gene names. This way transcripts (sublists) will get fused with contiguous sublists sharing the same gene name.
	gene = list(sublist_iterator[1])  #sublist_iterator[1] is a list of lists. Higher level lists are genes.
	if len(gene) == 1:					#One transcript by gene.
		output.append(">"+str(gene[0][0])+'\n'+str(gene[0][1]))
	else:								#len(gene) only equal or greater than 1. Can't be zero.
		longest_transcript = sorted(gene, key=lambda isoform: isoform[1], reverse = False) #sorted function, the key being the second field of the subsublist (i.e., the sequence)
		output.append(">"+str(longest_transcript[0][0])+'\n'+str(longest_transcript[0][1]))

for x in output:
	print(x)
"""

#Block of code to generate the file
with open(output_file,"w") as g:
	for sublist_iterator in groupby(sorted(fasta, key = lambda x: x[2]), lambda x: x[2]): #group sequences by gene names. Groupby works only on contiguous lines, so we need to sort the lists according to gene IDs. This way transcripts (sublists) will get fused with contiguous sublists sharing the same gene name.
		gene = list(sublist_iterator[1])	  #sublist_iterator[1] is a generator of lists. Higher level lists are genes.
		if len(gene) == 1:					#One transcript by gene.
			g.write(">"+str(gene[0][0])+'\n'+str(gene[0][1])+'\n')
		else:								#len(gene) only equal or greater than 1. Can't be zero.
			longest_transcript = sorted(gene, key=lambda isoform: len(isoform[1]), reverse = True) #sorted function, the key being the second field of the subsublist (i.e., the sequence length). In the event that several isoforms have the same length, the order within the source file prevails. 
			g.write(">"+str(longest_transcript[0][0])+'\n'+str(longest_transcript[0][1])+'\n')


